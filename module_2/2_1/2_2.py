import asyncio
import curses
import itertools
import random
import time
from typing import Tuple

from curses_tools import draw_frame, read_controls, get_frame_size
from space_garbage import fly_garbage


TIC_TIMEOUT = 0.1

CANVAS_FRAME_WIDTH = 1
MIN_CANVAS_COORDINATE = 0

STAR_X_WIDTH = 1
STAR_Y_WIDTH = 1


class AwaitableSleep:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)


def init_space_garbage_frames():
    with open('space_garbage_frames/trash_small.txt', 'r') as f:
        frame_1 = f.read()

    with open('space_garbage_frames/trash_xl.txt', 'r') as f:
        frame_2 = f.read()

    with open('space_garbage_frames/duck.txt', 'r') as f:
        frame_3 = f.read()

    with open('space_garbage_frames/hubble.txt', 'r') as f:
        frame_4 = f.read()

    with open('space_garbage_frames/lamp.txt', 'r') as f:
        frame_5 = f.read()

    with open('space_garbage_frames/trash_large.txt', 'r') as f:
        frame_6 = f.read()

    return frame_1, frame_2, frame_3, frame_4, frame_5, frame_6


space_garbage_small, space_garbage_xl, space_garbage_duck, space_garbage_hubble, space_garbage_lamp, space_garbage_large = init_space_garbage_frames()


def get_spaceship_frames(frame_1_name, frame_2_name) -> Tuple[str, str]:
    with open(frame_1_name, 'r') as f:
        frame_1 = f.read()

    with open(frame_2_name, 'r') as f:
        frame_2 = f.read()

    return frame_1, frame_2


frame_1, frame_2 = get_spaceship_frames('rocket_frame_1.txt', 'rocket_frame_2.txt')
frame_rows, frame_cols = get_frame_size(frame_1)


async def animate_spaceship(canvas, start_row, start_column):
    draw_frame(canvas, start_row, start_column, frame_1)

    for frame in itertools.cycle([frame_1, frame_2]):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        start_row, start_column = get_spaceship_new_yx(start_row, start_column, rows_direction, columns_direction, canvas)

        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


def get_spaceship_new_yx(start_row, start_column, rows_direction, columns_direction, canvas):
    max_y, max_x = canvas.getmaxyx()

    row = start_row + rows_direction  # y
    col = start_column + columns_direction  # x

    if row < MIN_CANVAS_COORDINATE:
        row = MIN_CANVAS_COORDINATE
    elif row >= (max_y - frame_rows):
        row = max_y - frame_rows - CANVAS_FRAME_WIDTH

    if col < MIN_CANVAS_COORDINATE:
        col = MIN_CANVAS_COORDINATE
    elif col >= max_x - frame_cols:
        col = max_x - frame_cols - CANVAS_FRAME_WIDTH

    return row, col



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
    max_row, max_column = rows - CANVAS_FRAME_WIDTH, columns - CANVAS_FRAME_WIDTH

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


sleeping_events = []


async def fill_orbit_with_garbage(canvas):
    _, max_x = canvas.getmaxyx()
    while True:
        global sleeping_events
        max_garbage_x = get_max_writable_x(max_x, 20)
        garbage_x = random.randint(MIN_CANVAS_COORDINATE, max_garbage_x)
        sleeping_events.append(
            [0, fly_garbage(canvas, garbage_x, space_garbage_small)]
        )
        await asyncio.sleep(0)




def get_max_writable_x(max_x: int, x_size: int) -> int:
    return max_x - CANVAS_FRAME_WIDTH - x_size


def get_max_writable_y(max_y: int, y_size: int) -> int:
    return max_y - CANVAS_FRAME_WIDTH - y_size


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

    global sleeping_events

    # STARS
    star_symbols = list('+*.:')
    max_star_y = get_max_writable_y(max_y, STAR_Y_WIDTH)
    max_star_x = get_max_writable_x(max_x, STAR_X_WIDTH)

    star_cores = []
    for i in range(300):
        y = random.randint(MIN_CANVAS_COORDINATE, max_star_y)
        x = random.randint(MIN_CANVAS_COORDINATE, max_star_x)
        symbol = random.choice(star_symbols)
        star_cor = blink(canvas, y, x, symbol)
        star_cores.append(star_cor)

    sleeping_events += [[0, star] for star in star_cores]

    # SPACESHIP FIRE
    sleeping_events.insert(0, [0, fire(canvas, max_y/2, max_x/2 + frame_cols/2)])

    # SPACESHIP
    sleeping_events.insert(0, [0, animate_spaceship(canvas, max_y/2, max_x/2)])

    # SPACE_GARBAGE
    # sleeping_events.insert(0, [0, fly_garbage(canvas, 0, space_garbage_small)])
    # sleeping_events.insert(0, [0, fly_garbage(canvas, 50, space_garbage_xl)])
    # sleeping_events.insert(0, [0, fly_garbage(canvas, 100, space_garbage_large)])
    # sleeping_events.insert(0, [0, fly_garbage(canvas, 100, space_garbage_hubble)])
    sleeping_events.insert(0, [0, fill_orbit_with_garbage(canvas)])

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
                seconds_to_sleep = getattr(sleep_command, 'seconds', TIC_TIMEOUT)
                sleeping_events.append([seconds_to_sleep, event[1]])
            canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
