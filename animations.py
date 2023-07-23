import curses
import itertools
import random
import time
import math

import helper
from helper import asleep
from constants import TIC_TIMEOUT
from constants import BORDER_SIZE

from physics import update_speed
from obstacles import Obstacle
from explosion import explode


obstacles = []
obstacles_in_last_collisions = set()


async def fire(canvas, start_row, start_col, rows_speed=-0.3, cols_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, col = start_row, start_col

    canvas.addstr(round(row), round(col), '*')
    await asleep(1)

    canvas.addstr(round(row), round(col), 'O')
    await asleep(1)
    canvas.addstr(round(row), round(col), ' ')

    row += rows_speed
    col += cols_speed

    symbol = '-' if cols_speed else '|'

    rows, cols = canvas.getmaxyx()
    max_row, max_col = rows - 1, cols - 1

    curses.beep()

    while BORDER_SIZE < row < max_row and BORDER_SIZE < col < max_col:
        for obstacle in obstacles:
            if obstacle.has_collision(row, col):
                obstacles_in_last_collisions.add(obstacle)
                return

        canvas.addstr(round(row), round(col), symbol)
        await asleep(1)
        canvas.addstr(round(row), round(col), ' ')
        row += rows_speed
        col += cols_speed


async def blink(canvas, row, col, symbol='*', timeout=0):
    await asleep(timeout)

    while True:
        canvas.addstr(row, col, symbol, curses.A_DIM)
        await asleep(int(2/TIC_TIMEOUT))

        canvas.addstr(row, col, symbol)
        await asleep(int(0.3/TIC_TIMEOUT))

        canvas.addstr(row, col, symbol, curses.A_BOLD)
        await asleep(int(0.5/TIC_TIMEOUT))

        canvas.addstr(row, col, symbol)
        await asleep(int(0.3/TIC_TIMEOUT))


async def draw_spaceship(canvas, coroutines, rocket_animation, presed_keys, window_size):
    rocket_frames = iter(itertools.cycle(rocket_animation))
    rocket_frame_rows_size, rocket_frame_cols_size = helper.get_frame_size(rocket_animation[0])
    center_point_row, center_point_col = window_size.rows // 2, window_size.cols // 2
    rocket_curent_row_coords, rocket_curent_col_coords = [
        center_point_row - rocket_frame_rows_size // 2,
        center_point_col - rocket_frame_cols_size // 2
    ]

    curent_rocket_animation_frame = next(rocket_frames)
    is_need_update_frame = False

    row_speed = column_speed = 0

    while True:
        for obstacle in obstacles:
            if obstacle.has_collision(rocket_curent_row_coords, rocket_curent_col_coords):
                return

        if is_need_update_frame:
            curent_rocket_animation_frame = next(rocket_frames)

        is_need_update_frame = not is_need_update_frame

        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            presed_keys[0],
            presed_keys[1],
        )

        max_rocket_row_coord = window_size.rows - BORDER_SIZE - rocket_frame_rows_size
        rocket_new_row_coord = rocket_curent_row_coords + row_speed
        rocket_curent_row_coords = min(max_rocket_row_coord, max(rocket_new_row_coord, BORDER_SIZE))

        max_rocket_col_coord = window_size.cols - BORDER_SIZE - rocket_frame_cols_size
        rocket_new_col_coord = rocket_curent_col_coords + column_speed
        rocket_curent_col_coords = min(max_rocket_col_coord, max(rocket_new_col_coord, BORDER_SIZE))

        if presed_keys[2]:
            coroutines.append(fire(
                canvas,
                rocket_new_row_coord,
                rocket_new_col_coord + math.floor(rocket_frame_cols_size / 2) + column_speed,
            ))

        helper.draw_frame(canvas, rocket_curent_row_coords, rocket_curent_col_coords, curent_rocket_animation_frame)

        await asleep(1)

        helper.draw_frame(
            canvas,
            rocket_curent_row_coords,
            rocket_curent_col_coords,
            curent_rocket_animation_frame,
            negative=True
        )


async def show_gameover(canvas):
    canvas_rows, canvas_cols = canvas.getmaxyx()
    # win = curses.newwin(100, 100, 10, 10)

    title = "game over"
    canvas.addstr(100, 100, title)
    canvas.refresh()

    while True:
        await asleep(1)


async def fly_garbage(canvas, col, garbage_frame, obstacle, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    canvas_rows, canvas_cols = canvas.getmaxyx()
    index_of_last_awaible_canvas_row = canvas_rows - 1

    garbage_height, garbage_width = helper.get_frame_size(garbage_frame)

    col = min(
        max(col, BORDER_SIZE),
        canvas_cols - BORDER_SIZE - garbage_width
    )

    # В первой итерации отрисуется нижняя строка фрейма, отрисуется на первой доступной строке, сразу под рамкой
    current_row = -garbage_height + 1 + BORDER_SIZE

    while current_row != index_of_last_awaible_canvas_row:
        helper.draw_frame(canvas, current_row, col, garbage_frame)
        await asleep(1)
        helper.draw_frame(canvas, current_row, col, garbage_frame, negative=True)

        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.discard(obstacle)
            obstacles.remove(obstacle)
            await explode(
                canvas,
                current_row + garbage_height // 2,
                col + garbage_width // 2,
            )
            return

        obstacle.row = current_row
        current_row += speed

    obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas, coroutines, garbage_frames, cols_count_without_border):
    while True:
        await asleep(10)

        col = random.randint(BORDER_SIZE, cols_count_without_border)
        garbage_frame = random.choice(garbage_frames)
        garbage_height, garbage_width = helper.get_frame_size(garbage_frame)

        obstacle = Obstacle(
            -garbage_height + 1 + BORDER_SIZE,
            col,
            garbage_height,
            garbage_width,
        )

        obstacles.append(obstacle)

        coroutines.append(fly_garbage(
            canvas,
            col,
            garbage_frame,
            obstacle,
        ))


async def draw_fps(canvas, row=BORDER_SIZE, col=BORDER_SIZE):
    fps = 0

    while True:
        previous_time = time.time_ns()
        await asleep(1)
        helper.draw_frame(canvas, row, col, f"{fps:0>6.2f} fps")
        fps = 1 / ((time.time_ns() - previous_time) / 10**9)
        helper.draw_frame(canvas, row, col, f"{fps:0>6.2f} fps")


async def draw_obstacles_counter(canvas, row=BORDER_SIZE + 1, col=BORDER_SIZE):
    while True:
        helper.draw_frame(canvas, row, col, f"{len(obstacles)} obstacles")
        await asleep(1)
