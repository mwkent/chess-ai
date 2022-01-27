import unittest
import chess
from board import Board
from search_extension_util import search_getting_mated
from constants import MAX_EVAL, MIN_EVAL

class TestSearchExtensionUtil(unittest.TestCase):

	def test_mate_in_1(self):
		board = Board("8/8/8/p1p5/P7/2k5/6q1/1K6 b - - 3 93")
		turn = chess.BLACK
		_, moves = search_getting_mated(board, turn, forced_mate_depth=1)
		self.assertEqual(moves, [chess.Move.from_uci("g2b2")])

	def test_mate_in_1_after_opponent_move(self):
		"""Opponent has three moves. All lead to mate in 1.
		"""
		board = Board("8/1q6/8/p1p5/P7/2k5/8/1K6 w - - 4 94")
		turn = chess.BLACK
		evaluation = search_getting_mated(board, turn, forced_mate_depth=1)
		self.assertEqual(evaluation[0], MAX_EVAL - 1)

	def test_mate_in_2(self):
		board = Board("1r3r1k/p1ppBbp1/3n2Q1/8/3p1P2/5R2/P5PP/7K w - - 2 26")
		turn = chess.BLACK
		evaluation = search_getting_mated(board, turn, forced_mate_depth=2)
		self.assertEqual(evaluation[0], MIN_EVAL + 2)

	def test_search_getting_mated(self):
		board = Board("5rk1/p1p1q3/5p1R/2p1p2Q/N7/pP2P3/K1P5/3r4 b - - 6 30")
		turn = chess.BLACK
		self.assertEqual(search_getting_mated(board, turn)[0], 0)

		# Mate in 2
		board = Board("3r2k1/p1p1q3/5p1R/2p1p2Q/N7/pP2P3/K1P5/3r4 w - - 7 31")
		turn = chess.BLACK
		self.assertEqual(search_getting_mated(board, turn)[0], MIN_EVAL + 2)

		# Mate in 1
		board = Board("3r2kR/p1p1q3/5p2/2p1p2Q/N7/pP2P3/K1P5/3r4 b - - 8 31")
		turn = chess.BLACK
		self.assertEqual(search_getting_mated(board, turn)[0], MIN_EVAL + 1)

		# Not every line leads to forced mate
		board = Board("8/pppk4/8/8/8/8/8/1KR4R w - - 0 1")
		turn = chess.WHITE
		self.assertEqual(search_getting_mated(board, turn)[0], 0)


if __name__ == '__main__':
	unittest.main()
