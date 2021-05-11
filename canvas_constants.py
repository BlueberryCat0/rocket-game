CANVAS_FRAME_WIDTH = 1
MIN_CANVAS_COORDINATE = 0


def get_max_writable_x(max_x: int, x_size: int) -> int:
    return max_x - CANVAS_FRAME_WIDTH - x_size


def get_max_writable_y(max_y: int, y_size: int) -> int:
    return max_y - CANVAS_FRAME_WIDTH - y_size
