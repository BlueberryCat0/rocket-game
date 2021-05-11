import asyncio
import time
from typing import Generator
import types


"""
Тиканье бомбы с 0 задержкой
"""

# async def do_ticking(amount_of_ticks=5):
#     for _ in range(amount_of_ticks):
#         print('tick')
#         await asyncio.sleep(0)


# ticking = do_ticking()

# while True:
#     try:
#         ticking.send(None)
#     except StopIteration:
#         print('Boom')
#         break


"""
Тиканье бомбы с задержкой 1 и кастомным Sleep
"""

# class EventLoopCommand:
#     def __await__(self):
#         return (yield self)


# class Sleep(EventLoopCommand):
#     def __init__(self, seconds: int):
#         self.seconds = seconds


# async def do_ticking(amount_of_ticks=5, sound: str):
#     for _ in range(amount_of_ticks):
#         print(sound)
#         await Sleep(1)


# async def bang_the_bomb():
#     clock = do_ticking()
#     await clock
#     print('Boom')


# bomb = bang_the_bomb()

# while True:
#     try:
#         sleep_command = bomb.send(None)
#         seconds_to_sleep = sleep_command.seconds
#         time.sleep(seconds_to_sleep)
#     except StopIteration:
#         break


"""
Взрываем много бомб
"""


class EventLoopCommand:
    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):
    def __init__(self, seconds: int):
        self.seconds = seconds


async def do_ticking(amount_of_ticks: int, sound: str):
    for _ in range(amount_of_ticks):
        print(sound)
        await Sleep(1)


async def bang_the_bomb(amount_of_ticks: int, sound: str):
    clock = do_ticking(amount_of_ticks, sound)
    await clock
    print('Boom')


bombs = [
    bang_the_bomb(amount_of_ticks=3, sound='tick'),
    bang_the_bomb(amount_of_ticks=5, sound='chick'),
    bang_the_bomb(amount_of_ticks=9, sound='click'),
]


sleeping_bombs = [[0, bomb] for bomb in bombs]

while sleeping_bombs:
    # осторожно засыпаем так, чтобы не пропустить активацию бомб
    min_delay, _ = min(sleeping_bombs, key=lambda pair: pair[0])
    sleeping_bombs = [[timeout - min_delay, bomb] for timeout, bomb in sleeping_bombs]
    time.sleep(min_delay)

    # делим бомбы на активные и спящие
    active_bombs = [[timeout, bomb] for timeout, bomb in sleeping_bombs if timeout <= 0]
    sleeping_bombs = [[timeout, bomb] for timeout, bomb in sleeping_bombs if timeout > 0]

    for _, bomb in active_bombs:
        try:
            sleep_command = bomb.send(None)
        except StopIteration:
            continue  # выкидываем истощившуюся корутину
        seconds_to_sleep = sleep_command.seconds
        sleeping_bombs.append([seconds_to_sleep, bomb])
