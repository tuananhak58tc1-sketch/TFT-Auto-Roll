from vision.screen_capture import ScreenCapture
from auto_roller import AutoRoller

def main():
    print("=== TFT AUTO ROLL ===")
    capture = ScreenCapture()
    
    # Tìm cửa sổ game
    windows = capture.get_window_list()
    if not windows:
        print("Không tìm thấy cửa sổ nào đang mở.")
        return
        
    print("\nDanh sách các cửa sổ:")
    for i, win in enumerate(windows):
        print(f"{i}: {win['title']}")
        
    try:
        idx = int(input("\nNhập số thứ tự của cửa sổ TFT: "))
        hwnd = windows[idx]['hwnd']
    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ.")
        return

    # Khởi động Bot
    bot = AutoRoller(hwnd)
    bot.run()

if __name__ == "__main__":
    main()

