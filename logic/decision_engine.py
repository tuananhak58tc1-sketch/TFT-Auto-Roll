class DecisionEngine:
    def __init__(self):
        pass

    def decide(self, detected_champions, target_plan):
        """
        Ra quyết định dựa trên tướng tìm thấy và kế hoạch (Plan).
        - detected_champions: list các dict VD [{'name': 'akali', 'x': 500, 'y': 800}]
        - target_plan: list tên các tướng muốn mua VD ['akali', 'Karma']
        """
        # Chuẩn hóa tên thành chữ thường để so sánh không bị lỗi hoa/thường
        plan_lower = [name.lower() for name in target_plan]
        
        champions_to_buy = []
        for champ in detected_champions:
            if champ['name'].lower() in plan_lower:
                champions_to_buy.append(champ)
                
        # Nếu có ít nhất 1 tướng đúng kế hoạch -> MUA
        if len(champions_to_buy) > 0:
            return {
                'action': 'BUY',
                'targets': champions_to_buy
            }
            
        # Nếu không có tướng nào trúng kế hoạch -> ĐỔI CỬA HÀNG (ROLL)
        return {
            'action': 'ROLL'
        }

