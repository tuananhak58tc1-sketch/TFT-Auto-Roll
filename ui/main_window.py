import sys
import cv2
import datetime
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from vision.screen_capture import ScreenCapture

class ImageSelectWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.original_pixmap = None
        self.scaled_pixmap = None
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0

    def set_image(self, pixmap):
        self.original_pixmap = pixmap
        self.scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        if not self.scaled_pixmap.isNull() and not self.original_pixmap.isNull():
            self.scale_factor_x = self.original_pixmap.width() / self.scaled_pixmap.width()
            self.scale_factor_y = self.original_pixmap.height() / self.scaled_pixmap.height()
            
        self.setPixmap(self.scaled_pixmap)
        self.selection_start = None
        self.selection_end = None
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.scaled_pixmap:
            self.is_selecting = True
            pos = self._get_pixmap_pos(event.position().toPoint())
            self.selection_start = pos
            self.selection_end = pos
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.scaled_pixmap:
            pos = self._get_pixmap_pos(event.position().toPoint())
            self.selection_end = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.update()

    def _get_pixmap_pos(self, widget_pos):
        x_offset = (self.width() - self.scaled_pixmap.width()) // 2
        y_offset = (self.height() - self.scaled_pixmap.height()) // 2
        
        x = widget_pos.x() - x_offset
        y = widget_pos.y() - y_offset
        
        x = max(0, min(x, self.scaled_pixmap.width()))
        y = max(0, min(y, self.scaled_pixmap.height()))
        
        return QPoint(x, y)

    def get_selection_rect_original(self):
        if not self.selection_start or not self.selection_end:
            return None
            
        rect = QRect(self.selection_start, self.selection_end).normalized()
        
        orig_x = int(rect.x() * self.scale_factor_x)
        orig_y = int(rect.y() * self.scale_factor_y)
        orig_w = int(rect.width() * self.scale_factor_x)
        orig_h = int(rect.height() * self.scale_factor_y)
        
        if orig_w == 0 or orig_h == 0:
            return None
            
        return QRect(orig_x, orig_y, orig_w, orig_h)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selection_start and self.selection_end:
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            
            x_offset = (self.width() - self.scaled_pixmap.width()) // 2
            y_offset = (self.height() - self.scaled_pixmap.height()) // 2
            
            start = self.selection_start + QPoint(x_offset, y_offset)
            end = self.selection_end + QPoint(x_offset, y_offset)
            
            rect = QRect(start, end).normalized()
            painter.drawRect(rect)

    def resizeEvent(self, event):
        if self.original_pixmap:
            self.set_image(self.original_pixmap)
        super().resizeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TFT Auto Roll")
        self.resize(800, 700)
        
        self.screen_capture = ScreenCapture()
        self.current_bgr_image = None
        self.window_list = []
        
        self._setup_ui()
        self._refresh_windows()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("TFT Auto Roll - Phase 2")
        font = title_label.font()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        main_layout.addWidget(title_label)
        
        # Window Selection Area
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("Select TFT Window:"))
        self.window_combo = QComboBox()
        self.window_combo.setMinimumWidth(300)
        window_layout.addWidget(self.window_combo)
        
        self.refresh_btn = QPushButton("Refresh Windows")
        window_layout.addWidget(self.refresh_btn)
        
        self.capture_btn = QPushButton("Capture TFT")
        window_layout.addWidget(self.capture_btn)
        
        main_layout.addLayout(window_layout)
        
        # Image Display Area
        self.image_label = ImageSelectWidget()
        self.image_label.setMinimumSize(640, 360)
        self.image_label.setStyleSheet("background-color: black;")
        main_layout.addWidget(self.image_label, stretch=1)
        
        # Actions Area
        action_layout = QHBoxLayout()
        self.save_plan_btn = QPushButton("Save Plan Capture")
        action_layout.addWidget(self.save_plan_btn)
        main_layout.addLayout(action_layout)
        
        # Status Area
        self.status_label = QLabel("Status: No window selected")
        main_layout.addWidget(self.status_label)
        
        # Connect signals
        self.refresh_btn.clicked.connect(self._refresh_windows)
        self.capture_btn.clicked.connect(self._capture_window)
        self.save_plan_btn.clicked.connect(self._save_plan_capture)

    def _refresh_windows(self):
        self.window_list = self.screen_capture.get_window_list()
        self.window_combo.clear()
        for win in self.window_list:
            self.window_combo.addItem(f"{win['title']} (HWND: {win['hwnd']})")
        self.status_label.setText("Status: Windows refreshed")

    def _capture_window(self):
        idx = self.window_combo.currentIndex()
        if idx < 0 or idx >= len(self.window_list):
            self.status_label.setText("Status: Please select a valid window")
            return
            
        hwnd = self.window_list[idx]['hwnd']
        img_bgr = self.screen_capture.capture_window(hwnd)
        
        if img_bgr is not None:
            self.current_bgr_image = img_bgr
            
            # Convert BGR to RGB for QImage
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            self.image_label.set_image(pixmap)
            self.status_label.setText("Status: Window captured. Please select Plan region.")
        else:
            self.status_label.setText("Status: Failed to capture window. Maybe minimized or invalid.")

    def _save_plan_capture(self):
        if self.current_bgr_image is None:
            self.status_label.setText("Status: Please capture a window first")
            return
            
        rect = self.image_label.get_selection_rect_original()
        if not rect:
            self.status_label.setText("Status: Please select a region on the image")
            return
            
        # Crop the image
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        cropped = self.current_bgr_image[y:y+h, x:x+w]
        
        if cropped.size == 0:
            self.status_label.setText("Status: Invalid selection")
            return
            
        # Save the image
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/plan_capture_{timestamp}.png"
        cv2.imwrite(filename, cropped)
        
        self.status_label.setText(f"Status: Plan capture saved to {filename}")
