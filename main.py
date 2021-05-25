import asyncio
import curses
import itertools
import random
import time

from awaitable_sleep import AwaitableSleep
from canvas_constants import get_max_writable_x, MIN_CANVAS_COORDINATE
from curses_tools import draw_frame, read_controls
from game_scenario import get_garbage_delay_tics, PHRASES, DEFAULT_PHRASE
from obstacles import show_obstacles
from physics import update_speed
from space_garbage import space_garbage, fly_garbage
from spaceship import (
    spaceship_frame_1, spaceship_frame_2,
    spaceship_row_size, spaceship_col_size,
    add_fire_event,
    get_spaceship_new_yx,
    show_gameover,
)
from stars import get_star_coroutines


DEBUG = False

TIC_TIMEOUT = 0.1
YEAR_IN_SECONDS = 1.5

SPACE_GUN_INIT_AFTER_YEAR = 2020

sleeping_events = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957


class GameProgressWindowSettings:
    HEIGHT = 5
    WIDTH = 60
    BORDER_DELTA = 1

    CONTENT_START_ROW = HEIGHT // 2

    @classmethod
    def get_row_start(cls, max_y):
        return max_y - cls.BORDER_DELTA - cls.HEIGHT

    @classmethod
    def get_col_start(cls):
        return cls.BORDER_DELTA


async def animate_spaceship(canvas, start_row, start_column):
    draw_frame(canvas, start_row, start_column, spaceship_frame_1)

    row_speed = column_speed = 0

    for frame in itertools.cycle([spaceship_frame_1, spaceship_frame_2]):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if space_pressed and year > SPACE_GUN_INIT_AFTER_YEAR:
            await add_fire_event(canvas, start_row, start_column, sleeping_events, obstacles)

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
                sleeping_events.append([0, show_gameover(canvas)])

        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


async def fill_orbit_with_garbage(canvas):
    global sleeping_events
    global obstacles
    global year

    _, max_x = canvas.getmaxyx()
    while True:
        sleep_time = get_garbage_delay_tics(year)
        if not sleep_time:
            await AwaitableSleep(YEAR_IN_SECONDS)
            continue

        max_garbage_x = get_max_writable_x(max_x, 20)
        garbage_x = random.randint(MIN_CANVAS_COORDINATE, max_garbage_x)
        new_garbage_frame = random.choice(list(space_garbage.frames.values()))
        sleeping_events.append(
            [0, fly_garbage(canvas, garbage_x, new_garbage_frame, obstacles=obstacles)]
        )

        await AwaitableSleep(sleep_time)


async def tick_time():
    global year

    while True:
        await AwaitableSleep(YEAR_IN_SECONDS)
        year += 1


async def show_game_progress(canvas):
    global year

    while True:
        canvas.border()

        phrase = PHRASES.get(year, DEFAULT_PHRASE)
        content = f'Year - {year}: {phrase}'
        draw_frame(
            canvas,
            GameProgressWindowSettings.CONTENT_START_ROW, GameProgressWindowSettings.BORDER_DELTA,
            content,
        )
        await AwaitableSleep(1)
        draw_frame(
            canvas,
            GameProgressWindowSettings.CONTENT_START_ROW, GameProgressWindowSettings.BORDER_DELTA,
            content,
            negative=True,
        )


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

    game_progress_window = canvas.derwin(
        GameProgressWindowSettings.HEIGHT,
        GameProgressWindowSettings.WIDTH,
        GameProgressWindowSettings.get_row_start(max_y),
        GameProgressWindowSettings.get_col_start(),
    )

    global sleeping_events
    global obstacles
    global year

    # STARS
    star_cores = get_star_coroutines(canvas, 300)
    sleeping_events += [[0, star] for star in star_cores]

    # GAME PROGRESS BAR
    sleeping_events.append([0, show_game_progress(game_progress_window)])

    # YEAR TIMER
    sleeping_events.append([0, tick_time()])

    # SPACESHIP
    sleeping_events.append([0, animate_spaceship(canvas, max_y/2, max_x/2)])

    # SPACE GARBAGE
    sleeping_events.append([0, fill_orbit_with_garbage(canvas)])

    if DEBUG:
        # SHOW OBSTACLES
        sleeping_events.append([0, show_obstacles(canvas, obstacles)])

    while True:
        min_delay, _ = min(sleeping_events, key=lambda event: event[0])
        _sleeping_events = [[timeout - min_delay, event] for timeout, event in sleeping_events]
        time.sleep(min_delay)

        # split events on active and sleeping
        active_events = [[timeout, event] for timeout, event in _sleeping_events if timeout <= 0]
        _sleeping_events = [[timeout, event] for timeout, event in _sleeping_events if timeout > 0]

        # for save sleeping_events's original global id
        sleeping_events_cores = [event[1] for event in _sleeping_events]
        for event in sleeping_events[:]:
            if event[1] not in sleeping_events_cores:
                sleeping_events.remove(event)

        # recalc sleep time for sleeping events
        for event in sleeping_events:
            for sl_event in _sleeping_events:
                if event[1] == sl_event[1]:
                    event[0] = sl_event[0]

        for i, event in enumerate(active_events[:]):
            try:
                sleep_command = event[1].send(None)
            except StopIteration:
                pass
            else:
                seconds_to_sleep = getattr(sleep_command, 'seconds', TIC_TIMEOUT)
                sleeping_events.append([seconds_to_sleep, event[1]])

            canvas.refresh()
            game_progress_window.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
