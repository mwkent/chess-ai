import unittest
import uci
from board import Board


class TestUci(unittest.TestCase):

	def test_set_option(self):
		board = Board()
		line = "setoption name UCI_Chess960 value true"
		parts = line.split(' ')
		uci.set_option(parts, board)
		self.assertTrue(board.chess960)

		line = "setoption name UCI_Chess960 value false"
		parts = line.split(' ')
		uci.set_option(parts, board)
		self.assertFalse(board.chess960)

		# Test doesn't throw error
		line = "setoption name go_commands value {'movetime': 1000}"
		parts = line.split(' ')
		uci.set_option(parts, board)
				

if __name__ == '__main__':
	unittest.main()
