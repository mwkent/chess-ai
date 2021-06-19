import unittest
import chess
import move_calculator

class TestMoveCalculator(unittest.TestCase):

	def test(self):
		board = chess.Board("4k3/1p2b3/p1p3p1/P1P3P1/1PK5/8/8/8 w - - 52 142")
		max_think_time = .19
		max_depth = 10
		is_ponder = False
		print(move_calculator.calculate(board, max_think_time, max_depth, is_ponder))

if __name__ == '__main__':
    unittest.main()