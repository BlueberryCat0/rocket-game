import curses
import random
import time

from awaitable_sleep import AwaitableSleep
from canvas_constants import get_max_writable_x, MIN_CANVAS_COORDINATE
from curses_tools import draw_frame
from game_scenario import get_garbage_delay_tics, PHRASES, DEFAULT_PHRASE
from obstacles import show_obstacles
from space_garbage import space_garbage, fly_garbage
from spaceship import animate_spaceship
from stars import get_star_coroutines

TIC_TIMEOUT = 0.1
YEAR_IN_SECONDS = 1.5

sleeping_events = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957


class GameProgressWindowSettings:
    HEIGHT = 5
    WIDTH = 60
    BORDER_DELTA = 1

    @classmethod
    def get_row_start(cls, max_y):
        return max_y - cls.BORDER_DELTA - cls.HEIGHT

    @classmethod
    def get_col_start(cls):
        return cls.BORDER_DELTA


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
            GameProgressWindowSettings.HEIGHT // 2, GameProgressWindowSettings.BORDER_DELTA,
            content,
        )
        await AwaitableSleep(1)
        draw_frame(
            canvas,
            GameProgressWindowSettings.HEIGHT // 2, GameProgressWindowSettings.BORDER_DELTA,
            content,
            negative=True,
        )


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

    game_progress_window = canvas.derwin(
        GameProgressWindowSettings.HEIGHT, GameProgressWindowSettings.WIDTH,
        GameProgressWindowSettings.get_row_start(max_y), GameProgressWindowSettings.get_col_start()
    )
    game_progress_window.border()

    global sleeping_events
    global obstacles
    global year

    # STARS
    star_cores = get_star_coroutines(canvas, 300)

    # SPACESHIP
    spaceship_core = animate_spaceship(
        canvas, max_y/2, max_x/2, sleeping_events, obstacles,
    )

    # SPACE GARBAGE
    garbage_init_core = fill_orbit_with_garbage(canvas)

    sleeping_events += [[0, star] for star in star_cores]
    sleeping_events.append([0, show_game_progress(game_progress_window)])
    sleeping_events.append([0, tick_time()])
    sleeping_events.append([0, spaceship_core])
    sleeping_events.append([0, garbage_init_core])
    sleeping_events.append([0, show_obstacles(canvas, obstacles)])

    while True:
        min_delay, _ = min(sleeping_events, key=lambda event: event[0])
        _sleeping_events = [[timeout - min_delay, event] for timeout, event in sleeping_events]
        time.sleep(min_delay)

        # делим евенты на активные и спящие
        active_events = [[timeout, event] for timeout, event in _sleeping_events if timeout <= 0]
        _sleeping_events = [[timeout, event] for timeout, event in _sleeping_events if timeout > 0]

        # Мув для сохранения одного id для sleeping_events
        # удаление активных евентов и списка спящих
        sleeping_events_cores = [event[1] for event in _sleeping_events]
        for event in sleeping_events[:]:
            if event[1] not in sleeping_events_cores:
                sleeping_events.remove(event)

        # пересчет времени для спящих
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
