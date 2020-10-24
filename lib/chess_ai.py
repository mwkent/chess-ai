import chess
import chess.pgn
from queue import PriorityQueue
from itertools import count
import minimax_alpha_beta


def print_pgn(board):
	game = chess.pgn.Game.from_board(board)
	print(game)

def print_move(move):
	print(board.san(move))


def play(board):
	while not board.is_game_over():
		move_to_make = minimax_alpha_beta.pick_move_with_sort(board)
		#move_to_make = minimax_alpha_beta.pick_move_ids(board, max_depth=3)
		print(board.san(move_to_make))
		board.push(move_to_make)


board = chess.Board()

play(board)
print()
print_pgn(board)

