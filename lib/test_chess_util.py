import unittest
import chess
import chess_util
from board import Board

class TestChessUtil(unittest.TestCase):

	def test_is_piece_on_light_square(self):
		piece = chess.A1
		self.assertFalse(chess_util.is_piece_on_light_square(piece))
		piece = chess.A2
		self.assertTrue(chess_util.is_piece_on_light_square(piece))

	def test_is_piece_on_dark_square(self):
		piece = chess.A1
		self.assertTrue(chess_util.is_piece_on_dark_square(piece))
		piece = chess.A2
		self.assertFalse(chess_util.is_piece_on_dark_square(piece))

	def test_on_light_squares(self):
		pieces = chess.SquareSet([chess.A1, chess.A2])
		self.assertTrue(chess_util.on_light_squares(pieces))
		pieces = chess.SquareSet.from_square(chess.A1)
		self.assertFalse(chess_util.on_light_squares(pieces))
		pieces = chess.SquareSet.from_square(chess.A2)
		self.assertTrue(chess_util.on_light_squares(pieces))

	def test_on_dark_squares(self):
		pieces = chess.SquareSet([chess.A1, chess.A2])
		self.assertTrue(chess_util.on_dark_squares(pieces))
		pieces = chess.SquareSet.from_square(chess.A1)
		self.assertTrue(chess_util.on_dark_squares(pieces))
		pieces = chess.SquareSet.from_square(chess.A2)
		self.assertFalse(chess_util.on_dark_squares(pieces))

	def test_get_diagonals(self):
		diagonal_squares = chess_util.get_diagonals(chess.A1)
		self.assertEqual(diagonal_squares, chess.SquareSet([chess.A1, chess.B2, chess.C3, chess.D4, chess.E5, chess.F6, chess.G7, chess.H8]))
		diagonal_squares = chess_util.get_diagonals(chess.C2)
		self.assertEqual(diagonal_squares, chess.SquareSet([chess.B1, chess.C2, chess.D3, chess.E4, chess.F5, chess.G6, chess.H7, chess.A4, chess.B3, chess.D1]))

	def test_get_adjacent_files(self):
		self.assertEqual(chess_util.get_adjacent_files(chess.A1), [1])
		self.assertEqual(chess_util.get_adjacent_files(chess.B1), [0, 2])
		self.assertEqual(chess_util.get_adjacent_files(chess.H8), [6])

	def test_get_file_squares(self):
		self.assertEqual(chess_util.get_file_squares(chess.A1), \
			chess.SquareSet([chess.A1, chess.A2, chess.A3, chess.A4, chess.A5, chess.A6, chess.A7, chess.A8]))
		self.assertEqual(chess_util.get_file_squares(chess.H7), \
			chess.SquareSet([chess.H1, chess.H2, chess.H3, chess.H4, chess.H5, chess.H6, chess.H7, chess.H8]))

	def test_get_file_and_rank_squares(self):
		file_and_rank_squares = chess_util.get_file_and_rank_squares(chess.A1)
		self.assertEqual(file_and_rank_squares, chess.SquareSet([chess.A1, chess.A2, chess.A3, chess.A4, chess.A5, chess.A6, chess.A7, chess.A8, \
			chess.B1, chess.C1, chess.D1, chess.E1, chess.F1, chess.G1, chess.H1]))
		file_and_rank_squares = chess_util.get_file_and_rank_squares(chess.B2)
		self.assertEqual(file_and_rank_squares, chess.SquareSet([chess.B1, chess.B2, chess.B3, chess.B4, chess.B5, chess.B6, chess.B7, chess.B8, \
			chess.A2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2]))

	def test_is_half_open_file(self):
		board = Board("k7/1p1p4/3P4/8/8/2P5/P1P5/K7 w - - 0 1")
		self.assertTrue(chess_util.is_half_open_file(board, chess.A1))
		self.assertTrue(chess_util.is_half_open_file(board, chess.B1))
		self.assertFalse(chess_util.is_half_open_file(board, chess.C1))
		self.assertFalse(chess_util.is_half_open_file(board, chess.D1))
		self.assertFalse(chess_util.is_half_open_file(board, chess.E1))

	def test_is_open_file(self):
		board = Board("k7/1p1p4/3P4/8/8/2P5/P1P5/K7 w - - 0 1")
		self.assertFalse(chess_util.is_open_file(board, chess.A1))
		self.assertFalse(chess_util.is_open_file(board, chess.B1))
		self.assertFalse(chess_util.is_open_file(board, chess.C1))
		self.assertFalse(chess_util.is_open_file(board, chess.D1))
		self.assertTrue(chess_util.is_open_file(board, chess.E1))

	def test_get_prior_pawn_square(self):
		pawn = chess.G5
		pawn_color = chess.BLACK
		prior_pawn_square = chess.G6
		self.assertEqual(chess_util.get_prior_pawn_square(pawn, pawn_color), prior_pawn_square)

		pawn_color = chess.WHITE
		prior_pawn_square = chess.G4
		self.assertEqual(chess_util.get_prior_pawn_square(pawn, pawn_color), prior_pawn_square)

	def test_get_adjusted_rank(self):
		square = chess.A1
		color = chess.WHITE
		adjusted_rank = chess_util.get_adjusted_rank(square, color)
		self.assertEqual(adjusted_rank, 0)
		square = chess.A1
		color = chess.BLACK
		adjusted_rank = chess_util.get_adjusted_rank(square, color)
		self.assertEqual(adjusted_rank, 7)
		square = chess.D5
		color = chess.BLACK
		adjusted_rank = chess_util.get_adjusted_rank(square, color)
		self.assertEqual(adjusted_rank, 3)

	def test_get_num_minor_pieces(self):
		board = Board()
		self.assertEqual(chess_util.get_num_minor_pieces(board, chess.WHITE), 4)

	def test_get_num_major_pieces(self):
		board = Board()
		self.assertEqual(chess_util.get_num_major_pieces(board, chess.WHITE), 3)

	def test_has_minor_or_major_pieces(self):
		board = Board()
		self.assertTrue(chess_util.has_minor_or_major_pieces(board, chess.WHITE))

	def test_has_only_knight_minor_or_major_pieces(self):
		board = Board()
		color = chess.WHITE
		self.assertFalse(chess_util.has_only_knight_minor_or_major_pieces(board, color))

		board = Board("8/1p4K1/1P6/5P2/1k6/8/8/n7 b - - 0 1")
		color = chess.WHITE
		self.assertFalse(chess_util.has_only_knight_minor_or_major_pieces(board, color))

		color = chess.BLACK
		self.assertTrue(chess_util.has_only_knight_minor_or_major_pieces(board, color))

	def test_get_min_valued_piece(self):
		board = Board()
		rook = chess.A1
		king = chess.E1
		pawn = chess.A2
		pieces = [pawn, rook]
		self.assertEqual(chess_util.get_min_valued_piece(board, pieces), pawn)

		pieces = [king]
		self.assertEqual(chess_util.get_min_valued_piece(board, pieces), king)

	def test_get_forward_knight_moves(self):
		board = Board("4k3/8/3p4/2p3p1/8/5N2/8/4K3 w - - 0 1")
		knight = chess.F3
		self.assertEqual(chess_util.get_forward_knight_moves(board, knight), [chess.D4, chess.H4, chess.E5, chess.G5])

	def test_is_or_can_claim_draw_stalemate(self):
		stalemate = Board("8/8/8/8/8/1q6/2k5/K7 w - - 0 1")
		self.assertTrue(chess_util.is_or_can_claim_draw(stalemate))

	def test_is_or_can_claim_draw_can_claim(self):
		board = Board()
		move1 = "g1f3"
		move2 = "g8f6"
		move3 = "f3g1"
		move4 = "f6g8"
		board.push_uci(move1)
		board.push_uci(move2)
		board.push_uci(move3)
		board.push_uci(move4)
		board.push_uci(move1)
		board.push_uci(move2)
		board.push_uci(move3)
		self.assertTrue(chess_util.is_or_can_claim_draw(board))

	def test_is_or_can_claim_draw_cannot_claim(self):
		board = Board()
		move1 = "g1f3"
		move2 = "g8f6"
		move3 = "f3g1"
		move4 = "f6g8"
		board.push_uci(move1)
		board.push_uci(move2)
		board.push_uci(move3)
		board.push_uci(move4)
		board.push_uci(move1)
		board.push_uci(move2)
		self.assertFalse(chess_util.is_or_can_claim_draw(board))

	def test_is_bishop_pinned(self):
		board = Board("4k3/8/8/8/8/3q4/3B4/3K4 w - - 0 1")
		bishop = chess.D2
		self.assertTrue(chess_util.is_bishop_pinned(board, bishop, chess.WHITE))

		board = Board("4k3/8/8/8/8/5q2/4B3/3K4 w - - 0 1")
		bishop = chess.E2
		self.assertFalse(chess_util.is_bishop_pinned(board, bishop, chess.WHITE))

	def test_is_rook_pinned(self):
		board = Board("4k3/8/8/8/8/5q2/4R3/3K4 w - - 0 1")
		rook = chess.E2
		self.assertTrue(chess_util.is_rook_pinned(board, rook, chess.WHITE))

		board = Board("4k3/8/8/8/8/3q4/3R4/3K4 w - - 0 1")
		rook = chess.D2
		self.assertFalse(chess_util.is_rook_pinned(board, rook, chess.WHITE))

	def test_count_attackers(self):
		board = Board("1kr5/8/8/3p4/4P3/2NRRB2/6N1/2KR3Q w - - 0 1")
		self.assertEqual(chess_util.count_attackers(board, chess.D5, chess.WHITE), 4)

	def test_get_pinner(self):
		board = Board("4k3/4r3/8/b7/8/8/3RP3/4K3 w - - 0 1")
		pinned_piece = chess.D2
		self.assertEqual(chess_util.get_pinner(board, pinned_piece), chess.A5)

		pinned_piece = chess.E2
		self.assertEqual(chess_util.get_pinner(board, pinned_piece), chess.E7)

	def test_get_num_pinner_and_pinned_piece_attacker_pairs(self):
		board = Board("rn2kb1r/pp2pppp/2p1b3/q7/3P4/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 8")
		pinned_side_attackers = [chess.A1, chess.C3]
		pinner_side_attackers = [chess.A5, chess.E6]
		piece = chess.A2
		self.assertEqual(chess_util.get_num_pinner_and_pinned_piece_attacker_pairs(board, pinned_side_attackers, pinner_side_attackers, piece), 1)
		self.assertEqual(chess_util.get_num_pinner_and_pinned_piece_attacker_pairs(board, pinner_side_attackers, pinned_side_attackers, piece), 0)

	def test_can_piece_be_captured(self):
		board = Board("6k1/5pb1/4BP2/8/8/8/6R1/5K2 w - - 0 1")
		piece = chess.E6
		self.assertTrue(chess_util.can_piece_be_captured(board, piece))

		piece = chess.F6
		self.assertFalse(chess_util.can_piece_be_captured(board, piece))

	def test_can_piece_capture(self):
		board = Board("6k1/5pb1/4BP2/8/8/8/6R1/5K2 w - - 0 1")
		attacking_piece = chess.F7
		attacked_piece = chess.E6
		self.assertTrue(chess_util.can_piece_capture(board, attacking_piece, attacked_piece))

		attacking_piece = chess.G7
		attacked_piece = chess.F6
		self.assertFalse(chess_util.can_piece_capture(board, attacking_piece, attacked_piece))

	def test_can_hanging_piece_be_captured(self):
		board = Board("2k5/8/4n3/b7/1q2R1P1/7P/4N3/K7 w - - 0 1")
		piece = chess.E4
		self.assertTrue(chess_util.can_hanging_piece_be_captured(board, piece))

		piece = chess.B4
		self.assertFalse(chess_util.can_hanging_piece_be_captured(board, piece))

	def test_can_hanging_piece_be_captured_by(self):
		board = Board("2k5/8/4n3/b7/1q2R1P1/7P/4N3/K7 w - - 0 1")
		attacking_piece = chess.E4
		attacked_piece = chess.B4
		self.assertFalse(chess_util.can_hanging_piece_be_captured_by(board, attacking_piece, attacked_piece))

		attacked_piece = chess.E2
		self.assertFalse(chess_util.can_hanging_piece_be_captured_by(board, attacking_piece, attacked_piece))

		attacked_piece = chess.E6
		self.assertTrue(chess_util.can_hanging_piece_be_captured_by(board, attacking_piece, attacked_piece))

		attacked_piece = chess.G4
		self.assertFalse(chess_util.can_hanging_piece_be_captured_by(board, attacking_piece, attacked_piece))

	def test_get_attackers(self):
		board = Board("1r2r1k1/p4pbp/q2p1np1/1ppPp3/1bB1P3/1QN2PPB/P6P/2BRK2R w K - 0 24")
		color = chess.WHITE
		square = chess.A2
		attackers = [chess.B3, chess.C4]
		self.assertEqual(chess_util.get_attackers(board, square, color), attackers)

	def test_get_first_attackers_and_defenders(self):
		board = Board("2k5/5p2/4p3/8/5N2/1B6/8/2K5 w - - 0 1")
		first_attackers = [chess.B3, chess.F4]
		first_defenders = [chess.F7]
		self.assertEqual(chess_util.get_first_attackers_and_defenders(board, chess.E6), (first_attackers, first_defenders))

	def test_get_battery_attackers(self):
		board = Board("2k5/8/4p3/5P2/6B1/8/4R3/2K1R3 w - - 0 1")
		attackers = [chess.E2, chess.F5]
		self.assertEqual(chess_util.get_battery_attackers(board, chess.E6, chess.WHITE, attackers), [chess.E1, chess.G4])

	def test_get_pinned_attackers_and_defenders(self):
		board = Board("rn2kb1r/pp2pppp/2p1b3/q7/3P4/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 8")
		piece = chess.A2
		pinned_attackers = []
		pinned_defenders = [chess.C3]
		self.assertEqual(chess_util.get_pinned_attackers_and_defenders(board, piece), (pinned_attackers, pinned_defenders))

	def test_get_second_attackers_and_defenders(self):
		board = Board("2k1r3/2qnr3/8/4p3/8/2B4B/1Q2R3/2K1R3 w - - 0 1")
		first_attackers = [chess.E2]
		first_defenders = [chess.C7, chess.E7]
		second_attackers = [chess.E1, chess.C3, chess.B2]
		second_defenders = [chess.E8]
		self.assertEqual(chess_util.get_second_attackers_and_defenders(board, chess.E5, first_attackers, first_defenders), \
			(second_attackers, second_defenders))

	def test_is_free_to_take(self):
		# Pawn can be taken with en passant
		board = Board("8/pR6/1p2k2p/6pP/6P1/2P5/r4PK1/8 w - g6 0 40")
		pawn = chess.G5
		attacked_square = chess.G6
		self.assertTrue(chess_util.is_free_to_take(board, pawn, attacked_square))

	def test_is_free_to_take_this_turn(self):
		board = Board("rnbqk1nr/pppp1ppp/4p3/7Q/3P4/b1P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		free_bishop = chess.A3
		self.assertTrue(chess_util.is_free_to_take_this_turn(board, free_bishop))
		defended_pawn = chess.F7
		self.assertFalse(chess_util.is_free_to_take_this_turn(board, defended_pawn))

		board = Board("rn2kb1r/pp2pppp/2p1b3/q7/3P4/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 8")
		defended_pawn = chess.A2
		self.assertFalse(chess_util.is_free_to_take_this_turn(board, defended_pawn))

		board = Board("2k5/5p2/4p3/8/5N2/1B6/8/2K5 w - - 0 1")
		defended_pawn = chess.E6
		self.assertFalse(chess_util.is_free_to_take_this_turn(board, defended_pawn))

		board = Board("1r2r1k1/p4pbp/q2p1np1/1ppPp3/1nP1P3/1QN2PPB/P6P/2BRK2R w K - 0 24")
		defended_pawn = chess.B5
		self.assertTrue(chess_util.is_free_to_take_this_turn(board, defended_pawn))

		# Pawn can be taken with en passant
		board = Board("8/pR6/1p2k2p/6pP/6P1/2P5/r4PK1/8 w - g6 0 40")
		pawn = chess.G5
		self.assertTrue(chess_util.is_free_to_take_this_turn(board, pawn))

	def test_get_most_valuable_free_to_take(self):
		board = Board("1Q2rrk1/p1p2ppp/5n2/3p4/3P4/1P3B1K/PB6/RN2Q3 b - - 0 21")
		self.assertIn(chess_util.get_most_valuable_free_to_take(board), [chess.E1, chess.B8])

	def test_get_most_valuable_free_to_trade(self):
		board = Board("r1bqkb1r/pppp1ppp/2n2n2/1B2p1P1/4P3/5N2/PPPP1P1P/RNBQK2R w KQkq - 0 1")
		self.assertEqual(chess_util.get_most_valuable_free_to_trade(board), (chess.F6, chess_util.PIECE_TYPES_TO_VALUES[chess.PAWN]))

		# Pinned pawn can't take bishop
		board = Board("1kr5/2p2p1p/p5qp/1p2P3/3r1b2/5NP1/PP5P/R1R3K1 w - - 0 24")
		self.assertEqual(chess_util.get_most_valuable_free_to_trade(board), (None, 0))

		board = Board("3r1q1k/1p2r1pb/pnp1B2p/8/P1QP2P1/1PNRPP2/2P2R1P/6K1 b - - 8 36")
		self.assertEqual(chess_util.get_most_valuable_free_to_trade(board), (chess.C4, chess_util.PIECE_TYPES_TO_VALUES[chess.KNIGHT]))


if __name__ == '__main__':
	unittest.main()
