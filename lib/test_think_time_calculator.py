import unittest
import think_time_calculator
from board import Board


class TestThinkTimeCalculator(unittest.TestCase):

    def test_endgame(self):
        board = Board("8/2p1n3/6pp/8/2k5/1r6/K7/8 b - - 25 101")
        wtime = 151_000
        winc = 5_000
        # 8:23
        btime = 506_000
        binc = 5_000
        think_time = think_time_calculator.get_max_think_time(
            board, wtime, winc, btime, binc)
        # print("endgame, 8:23 on clock =", think_time)
        self.assertTrue(think_time > 10)

    def test_start_position_blitz(self):
        board = Board()
        # 5+3 time
        wtime = 300_000
        winc = 3_000
        btime = 300_000
        binc = 3_000
        self.assertTrue(think_time_calculator.get_max_think_time(
            board, wtime, winc, btime, binc) > 3)

    def test_no_time_left(self):
        board = Board("1q6/6k1/5p1p/2p3p1/1p5r/1P1PP1PP/6QK/R7 b - - 23 84")
        wtime = 0
        winc = 0
        btime = 0
        binc = 0
        print(think_time_calculator.get_max_think_time(
            board, wtime, winc, btime, binc))
        self.assertTrue(think_time_calculator.get_max_think_time(
            board, wtime, winc, btime, binc) is not None)


if __name__ == '__main__':
    unittest.main()
