import curses
import random

from awaitable_sleep import AwaitableSleep
from canvas_constants import MIN_CANVAS_COORDINATE, get_max_writable_x, get_max_writable_y

STAR_X_WIDTH = 1
STAR_Y_WIDTH = 1
STAR_SYMBOLS = list('+*.:')


async def blink(canvas, row, column, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await AwaitableSleep(random.randint(0, 3))

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await AwaitableSleep(2)
        canvas.addstr(row, column, symbol)
        await AwaitableSleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await AwaitableSleep(0.5)

        canvas.addstr(row, column, symbol)
        await AwaitableSleep(0.3)


def get_star_coroutines(canvas, count):
    max_y, max_x = canvas.getmaxyx()
    max_star_y = get_max_writable_y(max_y, STAR_Y_WIDTH)
    max_star_x = get_max_writable_x(max_x, STAR_X_WIDTH)

    star_cores = []
    for _ in range(count):
        y = random.randint(MIN_CANVAS_COORDINATE, max_star_y)
        x = random.randint(MIN_CANVAS_COORDINATE, max_star_x)
        symbol = random.choice(STAR_SYMBOLS)
        star_cor = blink(canvas, y, x, symbol)
        star_cores.append(star_cor)

    return star_cores
