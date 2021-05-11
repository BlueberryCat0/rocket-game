from curses_tools import draw_frame
import asyncio
import random

from canvas_constants import get_max_writable_x, MIN_CANVAS_COORDINATE


class SpaceGarbage:
    FRAME_FILES = (
        'frames/space_garbage_frames/trash_small.txt',
        'frames/space_garbage_frames/trash_xl.txt',
        'frames/space_garbage_frames/duck.txt',
        'frames/space_garbage_frames/hubble.txt',
        'frames/space_garbage_frames/lamp.txt',
        'frames/space_garbage_frames/trash_large.txt'
    )

    frames: dict

    def __init__(self) -> None:
        self.frames = {
            self.get_garbage_name(frame): self.load_frame(frame)
            for frame in self.FRAME_FILES
        }

    @staticmethod
    def get_garbage_name(path: str) -> str:
        return path.split('/')[-1].split('.')[0]

    @staticmethod
    def load_frame(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()


space_garbage = SpaceGarbage()


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


# async def fill_orbit_with_garbage(canvas):
#     _, max_x = canvas.getmaxyx()
#     while True:
#         global sleeping_events
#         max_garbage_x = get_max_writable_x(max_x, 20)
#         garbage_x = random.randint(MIN_CANVAS_COORDINATE, max_garbage_x)
#         sleeping_events.append(
#             [0, fly_garbage(canvas, garbage_x, space_garbage_small)]
#         )
#         await asyncio.sleep(0)
