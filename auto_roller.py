import time
import pyautogui
import cv2
from vision.screen_capture import ScreenCapture
from vision.champion_recognizer import ChampionRecognizer
from logic.decision_engine import DecisionEngine

class AutoRoller:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.capture = ScreenCapture()
        self.shop_recognizer = ChampionRecognizer(templates_dir="data/templates/shop")
        self.planner_recognizer = ChampionRecognizer(templates_dir="data/templates/planner")
        self.engine = DecisionEngine()
        
        # Cấu hình PyAutoGUI
        pyautogui.PAUSE = 0.5 
        pyautogui.FAILSAFE = True

    def run(self):
        print("\n" + "="*40)
        print("🤖 AUTO ROLLER ĐÃ KHỞI ĐỘNG!")
        print("Tự động đọc Kế Hoạch (Team Planner) từ màn hình...")
        print("⚠ Đưa chuột lên GÓC TRÊN CÙNG BÊN TRÁI màn hình để DỪNG KHẨN CẤP!")
        print("Bấm Ctrl+C trên Terminal để thoát.")
        print("="*40 + "\n")
        
        # Đợi 3 giây để người dùng chuyển vào game
        for i in range(3, 0, -1):
            print(f"Bắt đầu trong {i} giây...")
            time.sleep(1)
            
        print("\n>>> ĐANG CHẠY AUTO... <<<")
        
        import keyboard
        current_plan = []
        is_rolling = False  # Trạng thái ban đầu: Chỉ đứng nhìn và lưu Plan

        try:
            while True:
                # Lắng nghe phím F2 để Bật/Tắt chế độ Roll
                if keyboard.is_pressed('f2'):
                    is_rolling = not is_rolling
                    if is_rolling:
                        print("\n▶️ [BẬT] ĐÃ NHẬN LỆNH! BẮT ĐẦU AUTO ROLL VÀ MUA TƯỚNG...")
                    else:
                        print("\n⏸️ [TẮT] ĐÃ DỪNG ROLL. CHUYỂN VỀ CHẾ ĐỘ CHỜ (Quét Kế Hoạch).")
                    time.sleep(0.3) # Chống dội phím (debounce)

                # 1. MẮT NHÌN: Chụp ảnh màn hình game
                img = self.capture.capture_window(self.hwnd)
                if img is None:
                    time.sleep(1)
                    continue

                # 2. ĐỌC KẾ HOẠCH (Luôn luôn đọc kể cả khi đang dừng Roll)
                detected_in_planner = self.planner_recognizer.find_champions_in_shop(img, threshold=0.75)
                new_plan = [champ['name'] for champ in detected_in_planner]
                
                if new_plan != current_plan:
                    current_plan = new_plan
                    print(f"\n🔄 Đã lưu Kế Hoạch mới: {current_plan}")
                    if not is_rolling:
                        print("   (Bấm phím F2 để bắt đầu Roll theo kế hoạch này)")
                
                # Nếu chưa có plan hoặc đang ở chế độ CHỜ thì không quét Shop
                if not current_plan or not is_rolling:
                    time.sleep(0.5)
                    continue

                # ==========================================
                # CHỈ CHẠY ĐOẠN DƯỚI ĐÂY KHI ĐÃ BẬT F2
                # ==========================================

                # 3. NHẬN THỨC: Tìm tướng trong shop
                found_champions = self.shop_recognizer.find_champions_in_shop(img, threshold=0.85)

                # 4. NÃO BỘ: Đưa ra quyết định
                decision = self.engine.decide(found_champions, current_plan)

                # 5. HÀNH ĐỘNG
                if decision['action'] == 'BUY':
                    print("=> CÓ HÀNG! Tiến hành MUA...")
                    # Mua tất cả các tướng đúng kế hoạch có trên màn hình
                    for target in decision['targets']:
                        x, y = target['x'], target['y']
                        print(f"   + Click mua {target['name']} tại ({x}, {y})")
                        
                        # Di chuyển chuột và click
                        # Lưu ý: Nếu window không ở chế độ Fullscreen gốc, tọa độ x, y này 
                        # là tọa độ tương đối của bức ảnh. Cần cộng thêm tọa độ của cửa sổ.
                        # Ở đây mss chụp theo tọa độ monitor vật lý nên x,y có thể cần điều chỉnh
                        # nếu x,y trả về từ matchTemplate là tọa độ trong bức ảnh.
                        
                        import win32gui
                        # Lấy tọa độ thực của góc trên cùng bên trái cửa sổ game
                        rect = win32gui.GetWindowRect(self.hwnd)
                        win_x, win_y = rect[0], rect[1]
                        
                        # Tọa độ thực trên màn hình = Tọa độ cửa sổ + Tọa độ trong ảnh
                        real_x = win_x + x
                        real_y = win_y + y
                        
                        pyautogui.click(real_x, real_y)
                        time.sleep(0.3) # Đợi animation mua
                        
                elif decision['action'] == 'ROLL':
                    print("=> Không có hàng ngon. Bấm phím D để ROLL!")
                    pyautogui.press('d')
                    # Đợi một chút cho hiệu ứng Roll hoàn tất và shop mới hiện ra
                    time.sleep(1.0)
                    
        except KeyboardInterrupt:
            print("\nĐã nhận lệnh dừng (Ctrl+C). Tắt Auto!")
        except pyautogui.FailSafeException:
            print("\nĐÃ DỪNG KHẨN CẤP! (Do chuột bị kéo vào góc màn hình)")

