import time
import curses
import asyncio

async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


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

  cores = [star_1, star_2, star_3, star_4, star_5]

  while True:
    for cor in cores:
      cor.send(None)
      canvas.refresh()
    time.sleep(0.5)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
