import cv2
import os
import numpy as np

class ChampionRecognizer:
    def __init__(self, templates_dir="data/templates/shop"):
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()

    def _preprocess_image(self, img_gray):
        """
        Tiền xử lý ảnh: Tạm thời giữ nguyên ảnh xám. 
        Phương pháp TM_CCOEFF_NORMED đã tự động bù trừ độ sáng.
        """
        return img_gray

    def _load_templates(self):
        """Tải toàn bộ ảnh mẫu từ thư mục templates vào bộ nhớ"""
        if not os.path.exists(self.templates_dir):
            return
            
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                champion_name = os.path.splitext(filename)[0]
                filepath = os.path.join(self.templates_dir, filename)
                
                # Đọc ảnh template
                template_img = cv2.imread(filepath)
                if template_img is not None:
                    # Chuyển sang ảnh xám
                    gray_template = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
                    # Áp dụng tiền xử lý (chỉ lấy chữ)
                    processed_template = self._preprocess_image(gray_template)
                    self.templates[champion_name] = processed_template
                    
        print(f"Đã tải {len(self.templates)} ảnh mẫu tướng (đã qua xử lý nền).")

    def find_champions_in_shop(self, shop_img, threshold=0.85):
        """
        Tìm kiếm các tướng có trong ảnh shop_img.
        Trả về danh sách dict chứa tên tướng và toạ độ trung tâm của thẻ tướng.
        """
        raw_matches = []
        if shop_img is None or len(self.templates) == 0:
            return raw_matches

        # Chuyển ảnh shop sang ảnh xám
        shop_gray = cv2.cvtColor(shop_img, cv2.COLOR_BGR2GRAY)
        processed_shop = self._preprocess_image(shop_gray)

        for champ_name, template_processed in self.templates.items():
            # Thực hiện Template Matching
            res = cv2.matchTemplate(processed_shop, template_processed, cv2.TM_CCOEFF_NORMED)
            
            # Lấy ra những vị trí có độ giống nhau (confidence) >= threshold
            loc = np.where(res >= threshold)
            h, w = template_processed.shape
            
            for pt in zip(*loc[::-1]):
                score = res[pt[1], pt[0]]
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2
                
                raw_matches.append({
                    'name': champ_name,
                    'x': center_x,
                    'y': center_y,
                    'score': score
                })

        # Lọc các kết quả trùng lặp (Non-Maximum Suppression)
        # Giữ lại kết quả có điểm số cao nhất cho mỗi khu vực
        found_champions = []
        # Sắp xếp theo điểm số giảm dần
        raw_matches.sort(key=lambda x: x['score'], reverse=True)
        
        for match in raw_matches:
            is_duplicate = False
            for existing in found_champions:
                # Nếu khoảng cách gần (< 50 pixel), đây là cùng một ô thẻ tướng
                if abs(existing['x'] - match['x']) < 50 and abs(existing['y'] - match['y']) < 50:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                found_champions.append(match)

        return found_champions
