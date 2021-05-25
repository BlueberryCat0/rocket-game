import curses
import time

from obstacles import show_obstacles
from space_garbage import fill_orbit_with_garbage
from spaceship import animate_spaceship
from stars import get_star_coroutines
from awaitable_sleep import AwaitableSleep

TIC_TIMEOUT = 0.1
YEAR_IN_SECONDS = 1.5

sleeping_events = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957


async def tick_time():
    global year

    while True:
        await AwaitableSleep(YEAR_IN_SECONDS)
        year += 1

        # print(year)


def draw(canvas):
    max_y, max_x = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

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
    garbage_init_core = fill_orbit_with_garbage(canvas, sleeping_events, obstacles, year)

    sleeping_events += [[0, star] for star in star_cores]
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


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
