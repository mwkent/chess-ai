import unittest
import chess
from board import Board


class TestBoard(unittest.TestCase):

	def test_copy(self):
		board = Board()
		board.push(chess.Move.from_uci("e2e4"))
		board.get_phase(chess.BLACK)
		board.get_attackers_and_defenders(chess.D2, chess.BLACK)
		
		board_copy = board.copy()
		self.assertEqual(board, board_copy)
		self.assertEqual(board._phase, board_copy._phase)
		self.assertEqual(board._squares_to_attackers_and_defenders,
						board_copy._squares_to_attackers_and_defenders)
		
		board.push(chess.Move.from_uci("e7e5"))
		board.get_phase(chess.WHITE)
		board.get_attackers_and_defenders(chess.D7, chess.WHITE)
		self.assertNotEqual(board, board_copy)
		self.assertNotEqual(board._phase, board_copy._phase)
		self.assertNotEqual(board._squares_to_attackers_and_defenders,
						board_copy._squares_to_attackers_and_defenders)

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

	def test_gives_checkmate(self):
		board = Board("rb2r3/pN2k1pp/1n1p1pn1/4P3/P7/4B1N1/qPPPP1PP/2K1RQ2 b - - 0 12")
		move = chess.Move.from_uci("a2a1")
		self.assertTrue(board.gives_checkmate(move))

		move = chess.Move.from_uci("a2b2")
		self.assertFalse(board.gives_checkmate(move))

	def test_get_castling_rook(self):
		board = Board("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
		move = chess.Move.from_uci("e1c1")
		rook_from_square = chess.A1
		rook_to_square = chess.D1
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		move = chess.Move.from_uci("e1g1")
		rook_from_square = chess.H1
		rook_to_square = chess.F1
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		board.push(chess.Move.null()) # Change to black's turn
		move = chess.Move.from_uci("e8c8")
		rook_from_square = chess.A8
		rook_to_square = chess.D8
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		move = chess.Move.from_uci("e8g8")
		rook_from_square = chess.H8
		rook_to_square = chess.F8
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

	def test_get_castling_rook_chess960(self):
		board = Board("4rkr1/pppppppp/8/8/8/8/PPPPPPPP/1RK2R2 w - - 0 1")
		board.chess960 = True
		move = chess.Move.from_uci("c1b1")
		rook_from_square = chess.B1
		rook_to_square = chess.D1
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		move = chess.Move.from_uci("c1f1")
		rook_from_square = chess.F1
		rook_to_square = chess.F1
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		board.push(chess.Move.null()) # Change to black's turn
		move = chess.Move.from_uci("f8e8")
		rook_from_square = chess.E8
		rook_to_square = chess.D8
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

		move = chess.Move.from_uci("f8g8")
		rook_from_square = chess.G8
		rook_to_square = chess.F8
		self.assertTrue(board.get_castling_rook(move), (rook_from_square, rook_to_square))

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

	def test_battery_through_opponents_piece(self):
		board = Board("1r3kn1/p3qppr/n3p3/3pP1Q1/1PpP1B1N/P1P1R3/2b1BPPP/R5K1 w - - 9 27")
		free_knight = chess.H4
		first_attackers = [chess.H7]
		second_attackers = [chess.E7]
		first_defenders = [chess.G5]
		second_defenders = []
		self.assertEqual(board.get_attackers_and_defenders(free_knight), \
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
