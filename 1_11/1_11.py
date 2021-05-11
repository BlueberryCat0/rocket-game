import time
import curses
import asyncio
import random
from typing import Tuple
import itertools

from curses_tools import draw_frame


TIC_TIMEOUT = 0.1


class AwaitableSleep:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)


def get_spaceship_frames(frame_1_name, frame_2_name) -> Tuple[str, str]:
    with open(frame_1_name, 'r') as f:
        frame_1 = f.read()

    with open(frame_2_name, 'r') as f:
        frame_2 = f.read()

    return frame_1, frame_2


frame_1, frame_2 = get_spaceship_frames('rocket_frame_1.txt', 'rocket_frame_2.txt')


async def animate_spaceship(canvas, start_row, start_column):
    draw_frame(canvas, start_row, start_column, frame_1)

    for frame in itertools.cycle([frame_1, frame_2]):
        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await asyncio.sleep(0)
    await AwaitableSleep(random.randint(0,3))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        await AwaitableSleep(2)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        await AwaitableSleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)
        await AwaitableSleep(0.5)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        await AwaitableSleep(0.3)


# async def blink(canvas, row, column, symbol='*'):
#     canvas.addstr(row, column, symbol, curses.A_DIM)
#     await asyncio.sleep(0)
#     await AwaitableSleep(random.randint(0,3))

#     while True:
#         canvas.addstr(row, column, '1', curses.A_DIM)
#         await asyncio.sleep(0)
#         await AwaitableSleep(2)

#         canvas.addstr(row, column, '2')
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.3)

#         canvas.addstr(row, column, '3', curses.A_BOLD)
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.5)

#         canvas.addstr(row, column, '4')
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.3)


def draw(canvas):
    stdscr = curses.initscr()
    max_y, max_x = stdscr.getmaxyx()
    star_symbols = list('+*.:')
    curses.curs_set(False)

    star_cores = []
    for i in range(100):
        y = random.randint(1, max_y-1)
        x = random.randint(1, max_x-1)
        symbol = random.choice(star_symbols)
        star_cor = blink(canvas, y, x, symbol)
        star_cores.append(star_cor)

    canvas.refresh()

    sleeping_events = [[0, star] for star in star_cores]

    # sleeping_events.insert(0, [0, fire(canvas, max_y/2, max_x/2)])

    sleeping_events.insert(0, [0, animate_spaceship(canvas, max_y/2, max_x/2)])

    while True:
        min_delay, _ = min(sleeping_events, key=lambda event: event[0])
        sleeping_events = [[timeout - min_delay, event] for timeout, event in sleeping_events]
        time.sleep(min_delay)

        # делим евенты на активные и спящие
        active_events = [[timeout, event] for timeout, event in sleeping_events if timeout <= 0]
        sleeping_events = [[timeout, event] for timeout, event in sleeping_events if timeout > 0]

        for i, event in enumerate(active_events[:]):
            try:
                sleep_command = event[1].send(None)
            except StopIteration:
                active_events.pop(i)
            else:
                canvas.refresh()
                seconds_to_sleep = getattr(sleep_command, 'seconds', TIC_TIMEOUT)
                sleeping_events.append([seconds_to_sleep, event[1]])

        # time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
