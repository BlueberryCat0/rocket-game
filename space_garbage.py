import asyncio

from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle


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


async def fly_garbage(canvas, column, garbage_frame, obstacles, speed=0.5):
    """
        Animate garbage, flying from top to bottom.
        Сolumn position will stay same, as specified on start.
    """
    from main import obstacles_in_last_collisions

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    row_size, col_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows_size=row_size, columns_size=col_size)
    obstacles.append(obstacle)

    while row < rows_number:
        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            break

    obstacles.remove(obstacle)
