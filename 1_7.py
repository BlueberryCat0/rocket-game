import time
import curses
import asyncio

TIC_TIMEOUT = 0.1


class AwaitableSleep:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __await__(self):
        return (yield self)


# async def blink(canvas, row, column, symbol='*'):

#     while True:
#         canvas.addstr(row, column, symbol, curses.A_DIM)
#         await asyncio.sleep(0)
#         await AwaitableSleep(2)

#         canvas.addstr(row, column, symbol)
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.3)

#         canvas.addstr(row, column, symbol, curses.A_BOLD)
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.5)

#         canvas.addstr(row, column, symbol)
#         await asyncio.sleep(0)
#         await AwaitableSleep(0.3)


async def blink(canvas, row, column, symbol='*'):

    while True:
        canvas.addstr(row, column, '1', curses.A_DIM)
        await asyncio.sleep(0)
        await AwaitableSleep(2)

        canvas.addstr(row, column, '2')
        await asyncio.sleep(0)
        await AwaitableSleep(0.3)

        canvas.addstr(row, column, '3', curses.A_BOLD)
        await asyncio.sleep(0)
        await AwaitableSleep(0.5)

        canvas.addstr(row, column, '4')
        await asyncio.sleep(0)
        await AwaitableSleep(0.3)


def draw(canvas):
    row_1, col_1 = (5, 5)
    row_2, col_2 = (5, 7)
    row_3, col_3 = (5, 9)
    row_4, col_4 = (5, 11)
    row_5, col_5 = (5, 13)

    star_1 = blink(canvas, row_1, col_1)
    star_2 = blink(canvas, row_2, col_2)
    star_3 = blink(canvas, row_3, col_3)
    star_4 = blink(canvas, row_4, col_4)
    star_5 = blink(canvas, row_5, col_5)
    canvas.refresh()

    star_cores = [star_1, star_2, star_3, star_4, star_5]
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
