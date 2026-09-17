import cv2
from vision.screen_capture import ScreenCapture
from vision.champion_recognizer import ChampionRecognizer

def test_recognition():
    print("Đang khởi tạo công cụ chụp màn hình...")
    capture = ScreenCapture()
    
    # Khởi tạo recognizer, nó sẽ tự load các ảnh trong data/templates/
    recognizer = ChampionRecognizer()
    
    # Tìm cửa sổ game
    windows = capture.get_window_list()
    if not windows:
        print("Không tìm thấy cửa sổ nào đang mở.")
        return
        
    print("\nDanh sách các cửa sổ:")
    for i, win in enumerate(windows):
        print(f"{i}: {win['title']}")
        
    try:
        idx = int(input("\nNhập số thứ tự của cửa sổ chứa game/ảnh TFT: "))
        hwnd = windows[idx]['hwnd']
    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ.")
        return

    import time
    print("Sẽ chụp ảnh trong 3 giây nữa! Hãy CHUYỂN NGAY sang cửa sổ game TFT nhé...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("Đang chụp ảnh cửa sổ...")
    img = capture.capture_window(hwnd)
    
    if img is None:
        print("Lỗi: Không thể chụp ảnh cửa sổ.")
        return
        
    # LƯU ẢNH DEBUG
    cv2.imwrite("debug_shop.png", img)
    print("Đã lưu ảnh bot nhìn thấy thành 'debug_shop.png'. Hãy mở file này lên xem có đúng là cửa sổ game không!")

    print("Đang quét tìm tướng...")
    
    # Debug: In ra độ giống nhau cao nhất của từng tướng
    shop_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_shop = recognizer._preprocess_image(shop_gray)
    print("\nChi tiết độ giống nhau (Confidence):")
    for champ_name, template_processed in recognizer.templates.items():
        res = cv2.matchTemplate(processed_shop, template_processed, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f" - {champ_name}: {max_val*100:.2f}%")
        
    found_champions = recognizer.find_champions_in_shop(img, threshold=0.85)
    
    print("\n" + "="*30)
    print(" KẾT QUẢ NHẬN DIỆN (Ngưỡng 85%)")
    print("="*30)
    if found_champions:
        print("Tìm thấy các tướng sau:")
        for champ in found_champions:
            print(f" - {champ['name']} (tại tọa độ X:{champ['x']}, Y:{champ['y']})")
    else:
        print("Không tìm thấy tướng nào vượt qua ngưỡng 70%.")
    print("="*30)

    # TEST LOGIC (Não bộ)
    from logic.decision_engine import DecisionEngine
    engine = DecisionEngine()
    
    # Giả sử kế hoạch của bạn chỉ muốn mua "Akali" và "Karma"
    my_plan = ["Akali", "Karma"]
    print(f"\nKẾ HOẠCH CỦA BẠN (PLAN): Muốn mua {my_plan}")
    
    decision = engine.decide(found_champions, my_plan)
    
    print("\n" + "="*30)
    print(" QUYẾT ĐỊNH CỦA BOT (LOGIC)")
    print("="*30)
    if decision['action'] == 'BUY':
        print("=> HÀNH ĐỘNG: MUA (CLICK CHUỘT)")
        for target in decision['targets']:
            print(f"   + Sẽ click vào {target['name']} tại ({target['x']}, {target['y']})")
    elif decision['action'] == 'ROLL':
        print("=> HÀNH ĐỘNG: ROLL (BẤM PHÍM D)")
    print("="*30)

if __name__ == "__main__":
    test_recognition()
