import curses
import random
import time

from awaitable_sleep import AwaitableSleep, AwaitableCoroAdder
from canvas_constants import MIN_CANVAS_COORDINATE, get_max_writable_x
from obstacles import show_obstacles
from space_garbage import fly_garbage, space_garbage
from spaceship import animate_spaceship, get_fire
from stars import get_star_coroutines

TIC_TIMEOUT = 0.1

sleeping_events = []

obstacles = []


async def fill_orbit_with_garbage(canvas):
    global sleeping_events
    global obstacles

    _, max_x = canvas.getmaxyx()
    while True:
        max_garbage_x = get_max_writable_x(max_x, 20)
        garbage_x = random.randint(MIN_CANVAS_COORDINATE, max_garbage_x)
        sleeping_events.append(
            [
                0,
                fly_garbage(
                    canvas, garbage_x, space_garbage.frames['trash_xl'], obstacles=obstacles,
                )
            ]
        )
        await AwaitableSleep(2)


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

    global sleeping_events
    global obstacles

    # STARS
    star_cores = get_star_coroutines(canvas, 300)

    # SPACESHIP
    spaceship_core = animate_spaceship(canvas, max_y/2, max_x/2)

    # SPACESHIP FIRE
    spaceship_fire_core = get_fire(canvas)

    # SPACE GARBAGE
    garbage_init_core = fill_orbit_with_garbage(canvas)

    sleeping_events += [[0, star] for star in star_cores]
    sleeping_events.append([0, spaceship_core])
    sleeping_events.append([0, spaceship_fire_core])
    sleeping_events.append([0, garbage_init_core])
    sleeping_events.append([0, show_obstacles(canvas, obstacles)])

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

                if isinstance(sleep_command, AwaitableCoroAdder):
                    sleeping_events.append(sleep_command.event)

            canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
