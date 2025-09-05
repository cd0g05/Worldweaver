
class CurrentAgent:
    def __init__(self):
        self.agent = 1

    def get_agent(self):
        return self.agent

    def advance_agent(self):
        self.agent = self.agent + 1


    def back_agent(self):
        self.agent = self.agent - 1

    def set_agent(self, stage):
        self.agent = stage
