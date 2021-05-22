from typing import Union


class AwaitableSleep:
    def __init__(self, seconds: Union[float, int]) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)
