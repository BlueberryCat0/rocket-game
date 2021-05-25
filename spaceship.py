import asyncio
import curses
import itertools

from canvas_constants import CANVAS_FRAME_WIDTH, MIN_CANVAS_COORDINATE
from curses_tools import draw_frame, read_controls, get_frame_size
from physics import update_speed


def get_frame(path: str) -> str:
    with open(path, 'r') as f:
        frame = f.read()
        return frame


spaceship_frame_1 = get_frame('frames/rocket/rocket_frame_1.txt')
spaceship_frame_2 = get_frame('frames/rocket/rocket_frame_2.txt')
spaceship_row_size, spaceship_col_size = get_frame_size(spaceship_frame_1)

gameover_frame = get_frame('frames/game_over.txt')


async def show_gameover(canvas):
    row_size, col_size = get_frame_size(gameover_frame)
    max_y, max_x = canvas.getmaxyx()
    frame_start_row = max_y / 2 - row_size
    frame_start_col = max_x / 2 - col_size / 2
    while True:
        draw_frame(
            canvas=canvas,
            start_row=frame_start_row,
            start_column=frame_start_col,
            text=gameover_frame,
        )
        await asyncio.sleep(0)


async def animate_spaceship(canvas, start_row, start_column, events, obstacles):
    draw_frame(canvas, start_row, start_column, spaceship_frame_1)
    await draw_spaceship_frames(canvas, start_row, start_column, events, obstacles)


async def draw_spaceship_frames(canvas, start_row, start_column, events, obstacles):
    row_speed = column_speed = 0

    for frame in itertools.cycle([spaceship_frame_1, spaceship_frame_2]):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if space_pressed:
            await add_fire_event(canvas, start_row, start_column, events, obstacles)

        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_direction, columns_direction,
        )

        start_row, start_column = get_spaceship_new_yx(
            start_row, start_column, row_speed, column_speed, canvas,
        )

        for obstacle in obstacles:
            if obstacle.has_collision(
                start_row, start_column, spaceship_row_size, spaceship_col_size
            ):
                events.append([0, show_gameover(canvas)])

        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


def get_spaceship_new_yx(
    start_row, start_column, rows_direction, columns_direction, canvas,
):

    max_y, max_x = canvas.getmaxyx()

    row = start_row + rows_direction  # y
    col = start_column + columns_direction  # x

    if row < MIN_CANVAS_COORDINATE:
        row = MIN_CANVAS_COORDINATE
    elif row >= (max_y - spaceship_row_size):
        row = max_y - spaceship_row_size - CANVAS_FRAME_WIDTH

    if col < MIN_CANVAS_COORDINATE:
        col = MIN_CANVAS_COORDINATE
    elif col >= max_x - spaceship_col_size:
        col = max_x - spaceship_col_size - CANVAS_FRAME_WIDTH

    return row, col


async def fire(canvas, start_row, start_column, obstacles, rows_speed=-0.3, columns_speed=0,):
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
        if check_hit(row, column, obstacles):
            break


def check_hit(fire_row, fire_column, obstacles: list) -> bool:
    from main import obstacles_in_last_collisions

    for obstacle in obstacles:
        if obstacle.has_collision(fire_row, fire_column):
            obstacles_in_last_collisions.append(obstacle)
            return True
    return False


def get_fire(canvas):
    max_y, max_x = canvas.getmaxyx()
    return fire(canvas, max_y/2, max_x/2 + spaceship_col_size/2)


async def add_fire_event(canvas, row, col, events, obstacles):
    event = [0, fire(canvas, row, col + spaceship_col_size/2, obstacles=obstacles)]
    events.append(event)
