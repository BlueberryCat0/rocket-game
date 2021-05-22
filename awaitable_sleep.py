from typing import Union


class AwaitableSleep:
    def __init__(self, seconds: Union[float, int]) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)


class AwaitableCoroAdder:
    """
    Из-за самодельного глобального евентлупа нет возможности добавлять корутины из иных файлов.
    """

    event: list
    seconds = 0

    def __init__(self, event: list) -> None:
        self.event = event

    def __await__(self):
        return (yield self)
