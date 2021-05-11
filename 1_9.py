import time
import curses
import asyncio
import random

TIC_TIMEOUT = 0.1


class AwaitableSleep:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)


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

    # star_cores = [star_1, star_2, star_3, star_4, star_5]
    sleeping_stars = [[0, star] for star in star_cores]

    while True:
        min_delay, _ = min(sleeping_stars, key=lambda star: star[0])
        sleeping_stars = [[timeout - min_delay, star] for timeout, star in sleeping_stars]
        time.sleep(min_delay)

        # делим звезды на активные и спящие
        active_stars = [[timeout, star] for timeout, star in sleeping_stars if timeout <= 0]
        sleeping_stars = [[timeout, star] for timeout, star in sleeping_stars if timeout > 0]

        for _, star in active_stars:
            sleep_command = star.send(None)
            canvas.refresh()
            seconds_to_sleep = getattr(sleep_command, 'seconds', 0)
            sleeping_stars.append([seconds_to_sleep, star])

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
