class SmallScreenError(Exception):
    def __init__(self, message="Screen size is too small"):
        self.message = message
        super().__init__(self.message)


class ExitGame(Exception):
    def __init__(self, message="Game exited"):
        self.message = message
        super().__init__(self.message)
