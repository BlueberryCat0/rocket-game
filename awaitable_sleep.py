class AwaitableSleep:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)
