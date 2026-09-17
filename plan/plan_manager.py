class PlanManager:
    def __init__(self):
        self.target_champions = []

    def add_champion(self, name):
        if name not in self.target_champions:
            self.target_champions.append(name)

    def get_plan(self):
        return self.target_champions

    def save_plan(self):
        # To be implemented
        pass

