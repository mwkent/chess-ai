import unittest
import chess
import think_time_calculator

class TestThinkTimeCalculator(unittest.TestCase):

	def test_endgame(self):
		board = chess.Board("8/2p1n3/6pp/8/2k5/1r6/K7/8 b - - 25 101")
		wtime = 151_000
		winc = 5_000
		# 8:23
		btime = 506_000
		binc = 5_000
		think_time = think_time_calculator.get_max_think_time(board, wtime, winc, btime, binc)
		#print("endgame, 8:23 on clock =", think_time)
		self.assertTrue(think_time > 10)


	# 5+3
	def test_start_position_blitz(self):
		board = chess.Board()
		wtime = 300_000
		winc = 3_000
		btime = 300_000
		binc = 3_000
		self.assertTrue(think_time_calculator.get_max_think_time(board, wtime, winc, btime, binc) > 3)


if __name__ == '__main__':
    unittest.main()