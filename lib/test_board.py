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

	def test_get_position_string(self):
		fen = "r3kbnr/pN1bq1p1/2p2p2/3p3p/P2Pn3/2P2N2/1P2PPPP/R1BQKB1R b KQkq - 0 15"
		position_string = "r3kbnr/pN1bq1p1/2p2p2/3p3p/P2Pn3/2P2N2/1P2PPPP/R1BQKB1R b KQkq -"
		board = Board(fen)
		self.assertEqual(board.get_position_string(), position_string)

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

	def test_get_moves_to_squares(self):
		board = Board("r1bqkb1r/2p1npp1/ppn1p2p/3pB2Q/3PP3/2NB1N2/PPP2PPP/3RK2R w Kkq - 0 10")
		bishop = chess.E5
		moves_to_squares = chess.SquareSet([chess.C7, chess.D6, chess.F6,
										chess.G7, chess.F4, chess.G3])
		self.assertEqual(board.get_moves_to_squares(bishop), moves_to_squares)

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

	def test_is_soft_pinned(self):
		board = Board("1k4n1/1r2qb2/4R1p1/2r5/1B1PN3/bN4n1/6R1/1K6 w - - 0 1")
		piece = chess.C5
		self.assertTrue(board.is_soft_pinned(piece))

		piece = chess.E6
		self.assertTrue(board.is_soft_pinned(piece))

		piece = chess.B4
		self.assertTrue(board.is_soft_pinned(piece))

		piece = chess.G3
		self.assertFalse(board.is_soft_pinned(piece))

		board = Board("5k2/3r1p1p/pr2q1p1/Rp1pPn2/3Pb3/1BP5/Q1PBR1PP/6K1 w - - 12 24")
		piece = chess.D5
		self.assertTrue(board.is_soft_pinned(piece))

	def test_is_attacker_soft_pinning(self):
		board = Board("1k4n1/1r2qb2/4R1p1/2r5/1B1PN3/bN4n1/6R1/1K6 w - - 0 1")
		attacker = chess.B4
		pinned_piece = chess.C5
		self.assertTrue(board.is_attacker_soft_pinning(attacker, pinned_piece))

		attacker = chess.F7
		pinned_piece = chess.E6
		self.assertTrue(board.is_attacker_soft_pinning(attacker, pinned_piece))

		attacker = chess.A3
		pinned_piece = chess.B4
		self.assertFalse(board.is_attacker_soft_pinning(attacker, pinned_piece))

		attacker = chess.G2
		pinned_piece = chess.G3
		self.assertFalse(board.is_attacker_soft_pinning(attacker, pinned_piece))

	def test_has_defender(self):
		board = Board("1k4n1/4qb2/4R3/2r5/1B1PN3/bN6/2R5/1K6 w - - 0 1")
		piece = chess.B4
		self.assertFalse(board.has_defender(piece))

		piece = chess.C5
		self.assertTrue(board.has_defender(piece))

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

	def test_get_soft_attackers_and_defenders(self):
		board = Board("rnbqk1nr/pppp1ppp/4p3/7Q/3P4/b1P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		free_bishop = chess.A3
		first_attackers = [chess.B2, chess.B1]
		second_attackers = [chess.C1]
		first_defenders = []
		second_defenders = []
		self.assertEqual(board.get_soft_attackers_and_defenders(free_bishop), \
			(first_attackers, second_attackers, first_defenders, second_defenders))
		# Test cached value
		self.assertEqual(board.get_soft_attackers_and_defenders(free_bishop), \
			(first_attackers, second_attackers, first_defenders, second_defenders))

		defended_pawn = chess.F7
		first_attackers = [chess.H5]
		second_attackers = []
		first_defenders = [chess.E8]
		second_defenders = []
		self.assertEqual(board.get_soft_attackers_and_defenders(defended_pawn), \
			(first_attackers, second_attackers, first_defenders, second_defenders))

		board = Board("rn2kb1r/pp2pppp/2p1b3/q7/3P4/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 8")
		defended_pawn = chess.A2
		first_attackers = [chess.E6, chess.A5]
		second_attackers = []
		first_defenders = [chess.A1]
		second_defenders = []
		self.assertEqual(board.get_soft_attackers_and_defenders(defended_pawn), \
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

	def test_is_stronger_piece_attacked_by(self):
		board = Board("rnb1kb1r/pp1p1ppp/q3pn2/2P5/4P3/2P2N2/PP1N1PPP/R1BQKB1R b KQkq - 0 6")
		attacking_piece = chess.F1
		attacked_piece = chess.A6
		self.assertTrue(board.is_stronger_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.F1
		attacked_piece = chess.B5
		self.assertFalse(board.is_stronger_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.B8
		attacked_piece = chess.A6
		self.assertFalse(board.is_stronger_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.F6
		attacked_piece = chess.E4
		self.assertFalse(board.is_stronger_piece_attacked_by(attacking_piece, attacked_piece))

		board = Board("r3kbnr/p2bq1p1/2pN1p2/3p3p/P2Pn3/5N2/1PP1PPPP/R1BQKB1R b KQkq - 2 15")
		attacking_piece = chess.D6
		attacked_piece = chess.E8
		self.assertFalse(board.is_stronger_piece_attacked_by(attacking_piece, attacked_piece))

	def test_get_stronger_pieces_attacked_by(self):
		board = Board("rnb1kb1r/pp1p1ppp/q3pn2/2P5/4P3/2P2N2/PP1N1PPP/R1BQKB1R b KQkq - 0 6")
		piece = chess.F1
		stronger_pieces = {chess.A6}
		self.assertEqual(board.get_stronger_pieces_attacked_by(piece), stronger_pieces)

		piece = chess.B8
		stronger_pieces = set()
		self.assertEqual(board.get_stronger_pieces_attacked_by(piece), stronger_pieces)

	def test_is_attacked_by_weaker_piece(self):
		board = Board("rnb1k3/pp1p1ppp/q3pn2/2P5/1b2r3/4BN2/PP1N1PPP/R1Q1KB1R b KQq - 0 6")
		piece = chess.A6
		self.assertTrue(board.is_attacked_by_weaker_piece(piece))

		piece = chess.E4
		self.assertFalse(board.is_attacked_by_weaker_piece(piece))

		piece = chess.C1
		self.assertFalse(board.is_attacked_by_weaker_piece(piece))

	def test_is_hanging_piece_attacked_by(self):
		board = Board("2k5/8/4n3/b7/1q2R1P1/7P/4N3/K7 w - - 0 1")
		attacking_piece = chess.E4
		attacked_piece = chess.E6
		self.assertTrue(board.is_hanging_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.E4
		attacked_piece = chess.B4
		self.assertFalse(board.is_hanging_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.E4
		attacked_piece = chess.E2
		self.assertFalse(board.is_hanging_piece_attacked_by(attacking_piece, attacked_piece))

		attacking_piece = chess.E4
		attacked_piece = chess.D4
		self.assertFalse(board.is_hanging_piece_attacked_by(attacking_piece, attacked_piece))

	def test_get_hanging_pieces_attacked_by(self):
		board = Board("2k5/8/4n3/b7/1q2R1P1/7P/4N3/K7 w - - 0 1")
		piece = chess.E4
		hanging_pieces = {chess.E6}
		self.assertEqual(hanging_pieces, board.get_hanging_pieces_attacked_by(piece))

	def test_does_piece_defend_attacked_piece(self):
		board = Board("rnb1kb1r/pp1p1ppp/4pn2/1qP5/1P6/2P2N2/P2NPPPP/R1BQKB1R b KQkq - 0 6")
		piece = chess.B4
		self.assertTrue(board.does_piece_defend_attacked_piece(piece))

		piece = chess.C1
		self.assertFalse(board.does_piece_defend_attacked_piece(piece))

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
