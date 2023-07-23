import time
import curses
import random

from collections import namedtuple
from pathlib import Path

import animations
import constants
import helper

from constants import TIC_TIMEOUT
from constants import BORDER_SIZE

Rectangle = namedtuple("Rectangle", ("rows", "cols"))

ROCKET_FRAMES_DIR  = Path("./rocket_frames")
GARBAGE_FRAMES_DIR = Path("./garbage_frames")


def draw(canvas):
	try:
		ROCKET_ANIMATION = helper.get_all_frames_in_dir(ROCKET_FRAMES_DIR)
	except helper.DirNotFoundError:
		print(
			f"Отсутсвет папка {ROCKET_FRAMES_DIR} в корневом"
			" каталоге проекта. Эта папка должна содержать"
			" кадры анимации космического корабля в формате"
			" текстовых файлов"
		)
		return
	except helper.FramesNotFoundError:
		print(f"В папке {ROCKET_FRAMES_DIR} отсутсвуют кадры анимации")
		return

	try:
		GARBAGE_FRAMES = helper.get_all_frames_in_dir(GARBAGE_FRAMES_DIR)
	except helper.DirNotFoundError:
		print(
			f"Отсутсвет папка {GARBAGE_FRAMES_DIR} в корневом"
			" каталоге проекта. Эта папка должна содержать"
			" изображения объектов мусора в формате"
			" текстовых файлов"
		)
		return
	except helper.FramesNotFoundError:
		print(f"В папке {GARBAGE_FRAMES_DIR} отсутсвуют кадры анимации")
		return

	curses.curs_set(False)
	canvas.border()
	canvas.nodelay(True)

	window_size = Rectangle(*canvas.getmaxyx())

	rows_count_without_border = window_size.rows - BORDER_SIZE * 2
	cols_count_without_border = window_size.cols - BORDER_SIZE * 2

	STARS_COUNT = int(
		constants.STARS_DENSITY *
		rows_count_without_border *
		cols_count_without_border
	)

	stars = [
		animations.blink(
			canvas,
			random.randint(BORDER_SIZE, rows_count_without_border),
			random.randint(BORDER_SIZE, cols_count_without_border),
			random.choice(constants.STARS_PICTURES),
			random.randint(0, constants.BLINK_ANIMATION_MAX_DELAY)
		)
		for _ in range(STARS_COUNT)
	]

	presed_keys = [0, 0, False]

	coroutines = [
		*stars,
		animations.draw_fps(canvas),
		animations.draw_obstacles_counter(canvas),
	]

	coroutines.append(animations.draw_spaceship(
		canvas,
		coroutines,
		ROCKET_ANIMATION,
		presed_keys,
		window_size=window_size
	))

	coroutines.append(animations.fill_orbit_with_garbage(
		canvas,
		coroutines,
		GARBAGE_FRAMES,
		cols_count_without_border
	))

	# coroutines.append(obstacles.show_obstacles(
	# 	canvas,
	# 	animations.obstacles,
	# ))

	while True:
		presed_keys[0], presed_keys[1], presed_keys[2] = helper.read_controls(canvas)

		for coroutine in coroutines.copy():
			try:
				coroutine.send(None)
			except StopIteration:
				coroutines.remove(coroutine)

		canvas.refresh()
		time.sleep(TIC_TIMEOUT)


curses.update_lines_cols()
curses.wrapper(draw)
