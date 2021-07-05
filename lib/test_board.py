import unittest
import chess
from board import Board


class TestBoard(unittest.TestCase):

	def test_get_phase_of_opening(self):
		board = Board()
		self.assertEqual(board.get_phase(chess.WHITE), 0)
		# Test cached value
		self.assertEqual(board.get_phase(chess.WHITE), 0)

	def test_get_phase_of_endgame(self):
		board = Board("8/8/6r1/2K5/4k3/8/6p1/8 w - - 0 69")
		self.assertEqual(board.get_phase(chess.BLACK), 1)
		# Test cached value
		self.assertEqual(board.get_phase(chess.BLACK), 1)

	def test_get_attackers_and_defenders(self):
		board = Board("rnbqk1nr/pppp1ppp/4p3/7Q/3P4/b1P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		free_bishop = chess.A3
		first_attackers = [chess.B2, chess.B1]
		second_attackers = [chess.C1]
		first_defenders = []
		second_defenders = []
		self.assertEqual(board.get_attackers_and_defenders(free_bishop), \
			(first_attackers, second_attackers, first_defenders, second_defenders))
		# Test cached value
		self.assertEqual(board.get_attackers_and_defenders(free_bishop), \
			(first_attackers, second_attackers, first_defenders, second_defenders))
		defended_pawn = chess.F7
		first_attackers = [chess.H5]
		second_attackers = []
		first_defenders = [chess.E8]
		second_defenders = []
		self.assertEqual(board.get_attackers_and_defenders(defended_pawn), \
			(first_attackers, second_attackers, first_defenders, second_defenders))

		board = Board("rn2kb1r/pp2pppp/2p1b3/q7/3P4/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 8")
		defended_pawn = chess.A2
		first_attackers = [chess.E6, chess.A5]
		second_attackers = []
		first_defenders = [chess.A1]
		second_defenders = [chess.C3]
		self.assertEqual(board.get_attackers_and_defenders(defended_pawn), \
			(first_attackers, second_attackers, first_defenders, second_defenders))

	def test_chess_960_castling(self):
		board = Board("rk6/pppb2rp/4p3/3pNp2/7R/1PP3P1/PKBP3P/R7 b q - 5 18", True)
		board.chess960 = True
		queenside_castle = chess.Move.from_uci("b8a8")
		self.assertTrue(queenside_castle in list(board.legal_moves))

		board = Board("rk6/pppb2rp/4p3/3pNp2/7R/1PP3P1/PKBP3P/R7 b q - 5 18", False)
		board.chess960 = True
		self.assertTrue(queenside_castle in list(board.legal_moves))


if __name__ == '__main__':
	unittest.main()
