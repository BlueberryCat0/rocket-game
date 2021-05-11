import curses
import asyncio
import itertools

from typing import Tuple

from curses_tools import draw_frame, read_controls, get_frame_size
from canvas_constants import CANVAS_FRAME_WIDTH, MIN_CANVAS_COORDINATE


def get_spaceship_frames(frame_1_name, frame_2_name) -> Tuple[str, str]:
    with open(frame_1_name, 'r') as f:
        frame_1 = f.read()

    with open(frame_2_name, 'r') as f:
        frame_2 = f.read()

    return frame_1, frame_2


frame_1, frame_2 = get_spaceship_frames('frames/rocket/rocket_frame_1.txt', 'frames/rocket/rocket_frame_2.txt')
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


def get_fire(canvas):
    max_y, max_x = canvas.getmaxyx()
    return fire(canvas, max_y/2, max_x/2 + frame_cols/2)
