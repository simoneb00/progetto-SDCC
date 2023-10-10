class Container:
    def __init__(self, id, alive_round=0,checked=True):
        self.id = id
        self.alive_round = alive_round
        self.checked = checked

    def pass_time(self):
        self.alive_round = self.alive_round + 1

    def reset_time(self):
        self.alive_round = 0

    def check(self):
        self.checked = True

    def reset(self):
        self.checked = False