import win32gui
import win32con
import mss
import numpy as np

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def get_window_list(self):
        """Returns a list of dicts with 'hwnd' and 'title' of visible windows."""
        windows = []
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Only add windows that have a title
                    windows.append({'hwnd': hwnd, 'title': title})
        
        win32gui.EnumWindows(enum_windows_callback, None)
        return windows

    def capture_window(self, hwnd):
        """Captures the window specified by hwnd and returns a numpy array (BGR)."""
        if not hwnd:
            return None
        
        # Get window rect (includes borders)
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            return None
            
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            return None
            
        monitor = {"top": top, "left": left, "width": width, "height": height}
        
        try:
            sct_img = self.sct.grab(monitor)
            # Convert mss image to numpy array in BGR format for cv2
            img_np = np.array(sct_img)
            # mss returns BGRA, drop the alpha channel
            img_bgr = img_np[:, :, :3]
            return img_bgr
        except mss.exception.ScreenShotError:
            return None
