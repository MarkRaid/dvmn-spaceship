import asyncio

from pathlib import Path


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


class DirNotFoundError(Exception):
    pass


class FramesNotFoundError(Exception):
    pass


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""
    
    rows_direction = cols_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            cols_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            cols_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, cols_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    count_rows, count_cols = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 1:
            continue

        if row >= count_rows - 1:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= count_cols:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == count_rows - 1 and column == count_cols - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    lines = text.splitlines()
    rows = len(lines)
    cols = max(map(len, lines))
    return rows, cols


def get_all_frames_in_dir_as_dict(path):
    if not path.exists():
        raise DirNotFoundError

    frames = {
        file.name: file.read_text()
        for file in filter(
            Path.is_file,
            path.iterdir()
        )
        if file.read_text()
    }

    if not frames:
        raise FramesNotFoundError

    return frames


def get_all_frames_in_dir(path):
    return list(get_all_frames_in_dir_as_dict(path).values())


async def asleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)
