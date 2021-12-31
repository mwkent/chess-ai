""""Handles calculating how much time the engine can think for
"""

from board import Board

def get_max_think_time(board: Board, white_time: int, white_increment: int,
					black_time: int, black_increment: int) -> float:
	"""Returns the max amount of time the engine can think for in seconds
	Parameters are passed in milliseconds
	"""
	player_time = white_time
	player_increment = white_increment
	if not board.turn:
		player_time = black_time
		player_increment = black_increment

	# Convert from milliseconds to seconds
	player_time /= 1000.0
	player_increment /= 1000.0

	# What is the most number of moves a game will take, roughly
	max_moves_in_game = 80
	min_moves_left = 20
	num_remaining_moves = max(max_moves_in_game - board.fullmove_number, min_moves_left)
	total_time_to_complete_game = player_time + num_remaining_moves * player_increment
	max_think_time = total_time_to_complete_game / num_remaining_moves

	if max_think_time == 0:
		max_think_time = 0.001

	return max_think_time

