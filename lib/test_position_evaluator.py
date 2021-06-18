import unittest
import chess
import position_evaluator

class TestPositionEvaluator(unittest.TestCase):

	def test_opposite_evaluations(self):
		board = chess.Board("rnbqkbnr/1p1ppppp/8/2p5/PpP5/8/3PPPPP/RNBQKBNR w KQkq - 0 4")
		self.assertEqual(position_evaluator.evaluate_position(board, chess.WHITE), -position_evaluator.evaluate_position(board, chess.BLACK))

	def test_mate_in_1(self):
		board = chess.Board("r1bqkbnr/1p1np2p/2P2p2/p5pQ/P2PP3/8/1P3PPP/RNB1KBNR b KQkq - 1 7")
		self.assertEqual(position_evaluator.evaluate_position(board, chess.WHITE), position_evaluator.MAX_EVAL)    	

	def test_connected_rooks(self):
		board = chess.Board("r4rk1/pbppqppp/1p3n2/2b5/4P3/2N3P1/PPP2PBP/R1BQ1RK1 w - - 7 11")
		self.assertEqual(position_evaluator.get_connected_rooks_value(board, chess.SquareSet([chess.F8, chess.A8])), position_evaluator.CONNECTED_ROOKS_EVAL)

	def test_disconnected_rooks(self):
		board = chess.Board("r3k2r/pbppqppp/1p3n2/2b5/4P3/2N3P1/PPP2PBP/R1BQ1RK1 b kq - 6 10")
		self.assertEqual(position_evaluator.get_connected_rooks_value(board, chess.SquareSet([chess.F8, chess.A8])), 0)

	def test_get_rook_on_open_file_bonus(self):
		board = chess.Board("5rk1/5ppp/4p3/8/8/8/5PPP/3RR1K1 w - - 0 1")
		rook = chess.D1
		self.assertEqual(position_evaluator.get_rook_on_open_file_bonus(board, rook), position_evaluator.ROOK_ON_OPEN_FILE_BONUS)

		rook = chess.E1
		self.assertEqual(position_evaluator.get_rook_on_open_file_bonus(board, rook), position_evaluator.ROOK_ON_HALF_OPEN_FILE_BONUS)

		rook = chess.F1
		self.assertEqual(position_evaluator.get_rook_on_open_file_bonus(board, rook), 0)

	def test_get_rook_too_aggressive_penalty(self):
		board = chess.Board("3qkb1r/pppp1ppp/2n2n2/4p3/R3P2r/4RN2/PPPP1PPP/2BQ2K1 w k - 0 1")
		rook = chess.A4
		self.assertEqual(position_evaluator.get_rook_too_aggressive_penalty(board, rook), position_evaluator.ROOK_TOO_AGGRESSIVE_PENALTY)

		rook = chess.E3
		self.assertEqual(position_evaluator.get_rook_too_aggressive_penalty(board, rook), 0)

		rook = chess.H4
		self.assertEqual(position_evaluator.get_rook_too_aggressive_penalty(board, rook), 0)

	def test_get_rook_aligned_with_bishop_penalty(self):
		board = chess.Board("5rk1/p1pqpp1p/2n2np1/3p1b2/1r6/2NPP1PP/P1PB1PBR/R2Q1K2 w - - 1 15")
		rook = chess.B4
		self.assertEqual(position_evaluator.get_rook_aligned_with_bishop_penalty(board, rook), position_evaluator.ROOK_ALIGNED_PENALTY)

		rook = chess.H2
		self.assertEqual(position_evaluator.get_rook_aligned_with_bishop_penalty(board, rook), 0)

	def test_rook_pinned_by_bihsop(self):
		board = chess.Board("5k2/8/8/8/5b2/8/3R4/2K5 w - - 0 1")
		turn = chess.WHITE
		self.assertTrue(position_evaluator.get_rook_value(board, turn) < 400)

	def test_is_isolated_pawn(self):
		pawns = chess.SquareSet([chess.A2, chess.B2, chess.D3, chess.H4])
		pawn = chess.A2
		self.assertFalse(position_evaluator.is_isolated_pawn(pawns, pawn))

		pawn = chess.B2
		self.assertFalse(position_evaluator.is_isolated_pawn(pawns, pawn))

		pawn = chess.D3
		self.assertTrue(position_evaluator.is_isolated_pawn(pawns, pawn))

		pawn = chess.H4
		self.assertTrue(position_evaluator.is_isolated_pawn(pawns, pawn))

	def test_no_isolated_pawns(self):
		self.assertEqual(position_evaluator.get_num_isolated_pawns(chess.SquareSet([chess.A2, chess.B2, chess.C2, chess.D4, chess.E2, chess.F2, chess.G2, chess.H2])), 0)		

	def test_isolated_pawns(self):
		self.assertEqual(position_evaluator.get_num_isolated_pawns(chess.SquareSet([chess.A2, chess.C5, chess.D4, chess.D6, chess.F2, chess.H2])), 3)

	def test_is_passed_pawn(self):
		board = chess.Board("4k3/p7/3pP3/3P4/1P6/8/7P/4K3 w - - 0 1")
		pawn = chess.A7
		self.assertFalse(position_evaluator.is_passed_pawn(board, pawn))		

		pawn = chess.B4
		self.assertFalse(position_evaluator.is_passed_pawn(board, pawn))		

		pawn = chess.D5
		self.assertFalse(position_evaluator.is_passed_pawn(board, pawn))		

		pawn = chess.D6
		self.assertFalse(position_evaluator.is_passed_pawn(board, pawn))		

		pawn = chess.E6
		self.assertTrue(position_evaluator.is_passed_pawn(board, pawn))		

		pawn = chess.H2
		self.assertTrue(position_evaluator.is_passed_pawn(board, pawn))		

	def test_get_adjusted_pawn_rank(self):
		self.assertEqual(position_evaluator.get_adjusted_pawn_rank(chess.A2, chess.WHITE), 0)
		self.assertEqual(position_evaluator.get_adjusted_pawn_rank(chess.A2, chess.BLACK), 5)

	def test_one_passed_pawn(self):
		board = chess.Board("4k3/p6p/8/8/8/8/4P3/2K5 w - - 0 1")
		self.assertEqual(position_evaluator.get_num_passed_pawns(board, chess.WHITE), 1)

	def test_two_passed_pawns(self):
		board = chess.Board("4k3/p6p/8/8/8/8/4P3/2K5 w - - 0 1")
		self.assertEqual(position_evaluator.get_num_passed_pawns(board, chess.BLACK), 2)

	def test_get_rook_behind_pawn_bonus(self):
		board = chess.Board("r3k3/8/5rp1/P7/8/8/R7/R3K3 w - - 0 1")
		pawn = chess.A5
		self.assertEqual(position_evaluator.get_rook_behind_pawn_bonus(board, pawn), \
			position_evaluator.ROOK_BEHIND_PAWN_BONUS + position_evaluator.ROOK_BEHIND_PAWN_PENALTY)

		pawn = chess.G6
		self.assertEqual(position_evaluator.get_rook_behind_pawn_bonus(board, pawn), 0)

	def test_king_safety_of_open_king(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n2q2/8/Q7/2P2NK1/P5PP/RN3BR1 b - - 3 13")
		turn = chess.WHITE
		percentage_attacked_adjacent = 3.0 / 8
		self.assertEqual(position_evaluator.get_king_safety(board, turn), \
			-percentage_attacked_adjacent * position_evaluator.get_eval(board, turn, position_evaluator.ATTACKING_ADJACENT_EVAL))

	def test_king_safety_of_safe_king(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n2q2/8/Q7/2P2NK1/P5PP/RN3BR1 b - - 3 13")
		percentage_attacked_adjacent = 0.0 / 8
		king_square_safety = position_evaluator.SQUARES_TO_BLACK_KING_SAFETY.get(chess.G8, 0)[0]
		color = chess.BLACK
		pawn_wall_value = 3 * position_evaluator.get_eval(board, color, position_evaluator.CLOSE_PAWN_WALL_EVAL)
		self.assertEqual(position_evaluator.get_king_safety(board, color), king_square_safety - percentage_attacked_adjacent + pawn_wall_value)

	def test_king_safety_of_king_in_check(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n3q1/8/Q7/2P2NK1/P5PP/RN3BR1 w - - 4 14")
		turn = chess.WHITE
		percentage_attacked_adjacent = 1.0 / 8
		self.assertEqual(position_evaluator.get_king_safety(board, turn), \
			-percentage_attacked_adjacent * position_evaluator.get_eval(board, turn, position_evaluator.ATTACKING_ADJACENT_EVAL))

	def test_center_pawn_eval(self):
		center_pawn_eval = 0
		self.assertEqual(position_evaluator.get_center_pawn_eval(chess.A2), center_pawn_eval)
		center_pawn_eval = position_evaluator.CENTRAL_PAWN_EVAL
		self.assertEqual(position_evaluator.get_center_pawn_eval(chess.B3), center_pawn_eval)

	def test_rank_pawn_eval_for_white(self):
		rank_pawn_eval = position_evaluator.RANK_PAWN_EVAL * 9
		pawn_squares = chess.SquareSet([chess.A2, chess.B3, chess.C5, chess.D7, chess.F2])
		self.assertEqual(position_evaluator.get_rank_pawn_eval(pawn_squares, chess.WHITE), rank_pawn_eval)

	def test_rank_pawn_eval_for_black(self):
		rank_pawn_eval = position_evaluator.RANK_PAWN_EVAL * 16
		pawn_squares = chess.SquareSet([chess.A2, chess.B3, chess.C5, chess.D7, chess.F2])
		self.assertEqual(position_evaluator.get_rank_pawn_eval(pawn_squares, chess.BLACK), rank_pawn_eval)

	def test_knight_rank_eval_for_white(self):
		knight_rank_eval = position_evaluator.KNIGHT_RANK_EVAL[4]
		knight_square = chess.C5
		self.assertEqual(position_evaluator.get_knight_rank_eval(knight_square, chess.WHITE), knight_rank_eval)

	def test_knight_rank_eval_for_black(self):
		knight_rank_eval = position_evaluator.KNIGHT_RANK_EVAL[3]
		knight_square = chess.C5
		self.assertEqual(position_evaluator.get_knight_rank_eval(knight_square, chess.BLACK), knight_rank_eval)

	# You cannot check if a king has castled from a FEN unless you do some analysis of the position. Not sure if it is helpful
	@unittest.skip("delete")
	def test_has_castled(self):
		board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		moves = ["e2e4", "e7e5", "f1e2", "a7a5", "g1f3", "b7b5", "e1g1"]
		for move in moves:
			board.push(chess.Move.from_uci(move))
		self.assertEqual(position_evaluator.has_castled(board, chess.WHITE), True)

	def test_get_phase_of_opening(self):
		board = chess.Board()
		self.assertEqual(position_evaluator.get_phase(board, chess.WHITE), 0)

	def test_get_phase_of_endgame(self):
		board = chess.Board("8/8/6r1/2K5/4k3/8/6p1/8 w - - 0 69")
		self.assertEqual(position_evaluator.get_phase(board, chess.BLACK), 1)

	def test_is_endgame(self):
		board = chess.Board("8/8/6r1/2K5/4k3/8/6p1/8 w - - 0 69")
		self.assertTrue(position_evaluator.is_endgame(board, chess.BLACK))

	def test_get_eval_for_endgame(self):
		board = chess.Board("8/8/6r1/2K5/4k3/8/6p1/8 w - - 0 69")
		test_range = [10, 20]
		self.assertEqual(position_evaluator.get_eval(board, chess.BLACK, test_range), test_range[1])

	def test_get_eval_for_value(self):
		board = chess.Board("8/8/6r1/2K5/4k3/8/6p1/8 w - - 0 69")
		test_value = 10
		self.assertEqual(position_evaluator.get_eval(board, chess.BLACK, test_value), test_value)

	# Need to figure this one out. It is complicated.
	@unittest.skip("delete")
	def test_free_knight(self):
		board = chess.Board("r1bqkb1r/ppp1pppp/5P2/8/3p4/2N5/PPP1PPPP/R1BQKB1R b KQkq - 0 6")
		evaluation = position_evaluator.evaluate_position(board, chess.BLACK)
		print("starting evaluation =", evaluation)
		print()
		board = chess.Board("r1bqkb1r/ppp2ppp/5p2/8/3p4/2N5/PPP1PPPP/R1BQKB1R w KQkq - 0 7")
		evaluation = position_evaluator.evaluate_position(board, chess.BLACK)
		print("took pawn evaluation =", evaluation)
		print()
		board = chess.Board("r1bqkb1r/ppp1pppp/5P2/8/8/2p5/PPP1PPPP/R1BQKB1R w KQkq - 0 7")
		evaluation = position_evaluator.evaluate_position(board, chess.BLACK)
		print("took knight evaluation =", evaluation)

	def test_get_queen_aligned_value(self):
		board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/1B2p1B1/4P3/5N2/PPP2PPP/RN1RK2Q w Qkq - 0 1")
		black_aligned_value = -2 * position_evaluator.QUEEN_ALIGNED_PENALTY
		self.assertEqual(position_evaluator.get_queen_aligned_value(board, chess.BLACK), black_aligned_value)
		white_aligned_value = 0
		self.assertEqual(position_evaluator.get_queen_aligned_value(board, chess.WHITE), white_aligned_value)

	# Queen pinned to king by rook or bishop
	def test_queen_pinned(self):
		# Queen pinned by bishop
		board = chess.Board("5k2/8/8/6p1/5b2/8/3Q4/2K5 w - - 0 1")
		turn = chess.WHITE
		self.assertTrue(position_evaluator.get_queen_value(board, turn) < 400)

		# Queen pinned by rook
		board = chess.Board("5k2/3p4/2r5/8/8/8/2Q5/2K5 w - - 0 1")
		turn = chess.WHITE
		self.assertTrue(position_evaluator.get_queen_value(board, turn) < 600)

	def test_is_piece_on_bishop_color(self):
		board = chess.Board("kb6/2b5/8/8/8/1BB5/P7/K7 w - - 0 1")
		piece = chess.A1
		self.assertTrue(position_evaluator.is_piece_on_bishop_color(board, piece))

		piece = chess.A2
		self.assertFalse(position_evaluator.is_piece_on_bishop_color(board, piece))

		# False because white has bishops on both colors
		piece = chess.A8
		self.assertFalse(position_evaluator.is_piece_on_bishop_color(board, piece))

	def test_bishop_pair_value(self):
		bishops = chess.SquareSet([chess.A1, chess.A2])
		self.assertEqual(position_evaluator.get_bishop_pair_value(bishops), position_evaluator.BISHOP_PAIR_EVAL)
		bishops = chess.SquareSet([chess.A1])
		self.assertEqual(position_evaluator.get_bishop_pair_value(bishops), 0)

	def test_developed_eval(self):
		knight = chess.B1
		color = chess.WHITE
		self.assertEqual(position_evaluator.get_developed_eval(knight, color), 0)
		knight = chess.F8
		color = chess.BLACK
		self.assertEqual(position_evaluator.get_developed_eval(knight, color), 0)
		knight = chess.B1
		color = chess.BLACK
		self.assertEqual(position_evaluator.get_developed_eval(knight, color), position_evaluator.DEVELOPMENT_BONUS)

	def test_long_diagonal_bonus(self):
		bishop = chess.B2
		self.assertEqual(position_evaluator.get_long_diagonal_bonus(bishop), position_evaluator.LONG_DIAGONAL_BONUS)
		bishop = chess.B1
		self.assertEqual(position_evaluator.get_long_diagonal_bonus(bishop), 0)

	def test_get_undeveloped_bishop_blocked_penalty(self):
		board = chess.Board("rnbqkbnr/ppp1pp1p/6p1/3p4/P1P1P3/1B6/1P1PQPPP/BN2KBNR w Kkq - 0 1")
		bishop = chess.A1
		self.assertEqual(position_evaluator.get_undeveloped_bishop_blocked_penalty(board, bishop), position_evaluator.BISHOP_BLOCKED_PENALTY)

		bishop = chess.B3
		self.assertEqual(position_evaluator.get_undeveloped_bishop_blocked_penalty(board, bishop), 0)

		bishop = chess.F1
		self.assertEqual(position_evaluator.get_undeveloped_bishop_blocked_penalty(board, bishop), position_evaluator.BISHOP_BLOCKED_PENALTY)

		bishop = chess.C8
		self.assertEqual(position_evaluator.get_undeveloped_bishop_blocked_penalty(board, bishop), 0)

		bishop = chess.F8
		self.assertEqual(position_evaluator.get_undeveloped_bishop_blocked_penalty(board, bishop), 0)

	def test_kick_knight_penalty(self):
		board = chess.Board("2k5/1ppp2p1/3b3p/3NN1b1/N4N2/6N1/8/2K5 w - - 0 1")
		knight = chess.A4
		self.assertEqual(position_evaluator.get_kick_knight_penalty(board, knight), position_evaluator.KICK_KNIGHT_PENALTY)

		knight = chess.D5
		self.assertEqual(position_evaluator.get_kick_knight_penalty(board, knight), position_evaluator.KICK_KNIGHT_PENALTY)

		knight = chess.E5
		self.assertEqual(position_evaluator.get_kick_knight_penalty(board, knight), 0)

		knight = chess.F4
		self.assertEqual(position_evaluator.get_kick_knight_penalty(board, knight), 0)

		knight = chess.G3
		self.assertEqual(position_evaluator.get_kick_knight_penalty(board, knight), 0)

	def test_get_knight_controlled_penalty(self):
		board = chess.Board("4k3/8/3p4/2p3p1/8/5N2/8/4K3 w - - 0 1")
		knight = chess.F3
		self.assertEqual(position_evaluator.get_knight_controlled_penalty(board, knight), position_evaluator.KNIGHT_CONTROLLED_PENALTY * 4)

	def test_bishop_battery_bonus(self):
		board = chess.Board("2r3k1/b4pp1/p1p4p/1b3N2/QP2P3/2P2P2/P4qPP/R6K w - - 5 25")
		bishop = chess.A7
		color = chess.BLACK
		self.assertEqual(position_evaluator.get_bishop_battery_bonus(board, bishop, color), position_evaluator.BISHOP_BATTERY_BONUS)

		bishop = chess.B5
		color = chess.BLACK
		self.assertEqual(position_evaluator.get_bishop_battery_bonus(board, bishop, color), 0)


	def test_get_attacking_bonus(self):
		board = chess.Board("2r3k1/b4pp1/p1p4p/1b3N2/QP2P3/2P2P2/P4qPP/R6K w - - 5 25")
		color = chess.WHITE
		piece = chess.F5
		center_count = 1
		second_ring_count = 2
		third_ring_count = 3
		second_rank_count = 4
		third_rank_count = 2
		fourth_rank_count = 2
		attacking_bonus = center_count * position_evaluator.SQUARES_TO_ATTACKING_BONUS.get(position_evaluator.CENTER[0])[0] + \
			second_ring_count * position_evaluator.SQUARES_TO_ATTACKING_BONUS.get(position_evaluator.SECOND_RING[0])[0] + \
			third_ring_count * position_evaluator.SQUARES_TO_ATTACKING_BONUS.get(position_evaluator.THIRD_RING[0])[0] + \
			second_rank_count * position_evaluator.RANKS_TO_ATTACKING_BONUS.get(2)[0] + \
			third_rank_count * position_evaluator.RANKS_TO_ATTACKING_BONUS.get(4)[0] + \
			fourth_rank_count * position_evaluator.RANKS_TO_ATTACKING_BONUS.get(6)[0]
		self.assertEqual(position_evaluator.get_attacking_bonus(board, color, piece), attacking_bonus)

	def test_get_pressure_penalty(self):
		board = chess.Board("r4rk1/2pqpp1p/1pn3p1/p2pbb2/6n1/P2PPNP1/1PP1NPBP/R1BQ1R1K w - - 0 13")
		piece = chess.E5
		self.assertEqual(position_evaluator.get_pressure_penalty(board, piece), 0)

		piece = chess.B2
		self.assertEqual(position_evaluator.get_pressure_penalty(board, piece), position_evaluator.PRESSURE_PENALTY)

		piece = chess.F2
		self.assertEqual(position_evaluator.get_pressure_penalty(board, piece), position_evaluator.PRESSURE_PENALTY)

	def test_can_knight_catch_pawn(self):
		board = chess.Board("8/1p4K1/1P6/5P2/1k6/8/8/1n6 w - - 0 1")
		pawn = chess.F5
		knight = chess.B1
		self.assertFalse(position_evaluator.can_knight_catch_pawn(board, knight, pawn))

		board = chess.Board("8/1p4K1/1P6/5P2/1k6/8/2n5/8 w - - 0 1")
		pawn = chess.F5
		knight = chess.C2
		self.assertTrue(position_evaluator.can_knight_catch_pawn(board, knight, pawn))

		board = chess.Board("8/1p4K1/1P6/5P2/1k6/8/8/n7 b - - 0 1")
		pawn = chess.F5
		knight = chess.A1
		self.assertTrue(position_evaluator.can_knight_catch_pawn(board, knight, pawn))

	def test_is_pawn_promoting(self):
		board = chess.Board("8/8/1ppp4/6P1/k7/8/8/5K2 w - - 0 1")
		pawn = chess.G5
		color = chess.WHITE
		self.assertTrue(position_evaluator.is_pawn_promoting(board, pawn, color))

		board = chess.Board("8/8/1ppp4/3k2P1/8/8/8/5K2 w - - 0 1")
		pawn = chess.G5
		color = chess.WHITE
		self.assertFalse(position_evaluator.is_pawn_promoting(board, pawn, color))

		# King controls queening square and squares in front of pawn
		board = chess.Board("8/1p2k1K1/1P6/5P2/8/8/8/8 w - - 0 1")
		pawn = chess.F5
		color = chess.WHITE
		self.assertTrue(position_evaluator.is_pawn_promoting(board, pawn, color))

		board = chess.Board("8/1p4K1/1P6/5P2/1k6/8/8/1n6 w - - 0 1")
		pawn = chess.F5
		color = chess.WHITE
		self.assertTrue(position_evaluator.is_pawn_promoting(board, pawn, color))

	def test_get_pawn_promoting_bonus(self):
		board = chess.Board("8/2q1k1P1/8/8/8/8/8/5K2 w - - 0 1")
		pawn = chess.G7
		color = chess.WHITE
		self.assertEqual(position_evaluator.get_pawn_promoting_bonus(board, pawn, color), position_evaluator.PAWN_PROMOTING_RANK_BONUS[5])

		board = chess.Board("8/2q2kP1/8/8/8/8/8/5K2 w - - 0 1")
		pawn = chess.G7
		color = chess.WHITE
		self.assertEqual(position_evaluator.get_pawn_promoting_bonus(board, pawn, color), 0)

	def test_get_promotion_support_bonus(self):
		board = chess.Board("2k5/8/K4n2/1P4p1/8/4N3/8/8 w - - 0 1")
		pawn = chess.B5
		self.assertEqual(position_evaluator.get_promotion_support_bonus(board, pawn), position_evaluator.DEFENDING_SQUARE_IN_FRONT_OF_PAWN_BONUS)

		pawn = chess.G5
		self.assertEqual(position_evaluator.get_promotion_support_bonus(board, pawn), 0)

	def test_get_defended_bonus(self):
		board = chess.Board("rnbqk1nr/pppp1ppp/4p3/8/1b1PP3/2N2NP1/PPP2P1P/R1BQKB1R w KQkq - 0 1")
		self.assertEqual(position_evaluator.get_defended_bonus(board, chess.E4), 0)
		self.assertEqual(position_evaluator.get_defended_bonus(board, chess.D4), position_evaluator.DOUBLE_DEFENDED_BONUS)
		self.assertEqual(position_evaluator.get_defended_bonus(board, chess.F3), position_evaluator.DEFENDED_EVAL)
		self.assertEqual(position_evaluator.get_defended_bonus(board, chess.G3), position_evaluator.PAWN_DEFENDING_BONUS)

	def test_get_blockaded_pawn_penalty(self):
		board = chess.Board("8/2kB4/2P5/8/6N1/6p1/8/1K6 w - - 0 1")
		self.assertEqual(position_evaluator.get_blockaded_pawn_penalty(board, chess.C6), position_evaluator.BLOCKADED_PAWN_PENALTY)
		self.assertEqual(position_evaluator.get_blockaded_pawn_penalty(board, chess.G3), 0)
		
	# If turn is winning and can claim a draw, it will choose not to
	def test_turn_will_not_claim_draw_when_winning(self):
		turn = chess.WHITE
		board = chess.Board("2q4k/2n1Q1b1/2P4p/4P3/1PR5/8/5PPP/6K1 b - - 4 57")
		board.push_uci("g7f8")
		board.push_uci("e7f6")
		board.push_uci("f8g7")
		board.push_uci("f6e7")
		board.push_uci("g7f8")
		board.push_uci("e7f6")
		self.assertNotEqual(position_evaluator.evaluate_position(board, turn), position_evaluator.DRAW_EVAL)

	def test_get_knight_fork_value(self):
		board = chess.Board("4q3/8/5N2/8/2k3r1/4N3/4N3/2K3Q1 w - - 0 1")
		knight = chess.F6
		self.assertEqual(position_evaluator.get_knight_fork_value(board, knight), \
			position_evaluator.PIECE_TYPES_TO_VALUES[chess.ROOK] - position_evaluator.PIECE_TYPES_TO_VALUES[chess.KNIGHT])

		# Knight is free to take
		knight = chess.E3
		self.assertEqual(position_evaluator.get_knight_fork_value(board, knight), 0)

		# Forking own pieces does not count
		knight = chess.E2
		self.assertEqual(position_evaluator.get_knight_fork_value(board, knight), 0)

	# Pawn is free to trade for queen
	def test_get_queen_free_to_trade(self):
		board = chess.Board("6k1/5ppp/1p6/2pp4/1r2n3/4PNqP/2Q2PB1/4R1K1 w - - 0 41")
		turn = chess.BLACK
		self.assertEqual(position_evaluator.get_queen_value(board, turn, None, chess.G3, position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN]), \
			position_evaluator.FREE_TO_TRADE_MODIFIER * position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN])

	def test_activate_king(self):
		board = chess.Board("8/8/3k4/8/2PPP3/3K4/8/8 w - - 0 1")
		num_pawns = 3

		turn = chess.WHITE
		distance = 1
		self.assertEqual(position_evaluator.activate_king(board, turn), position_evaluator.KING_DISTANCE_TO_PAWN_BONUS[1] * (7-distance) * num_pawns)

		turn = chess.BLACK
		distance = 2
		self.assertEqual(position_evaluator.activate_king(board, turn), position_evaluator.KING_DISTANCE_TO_PAWN_BONUS[1] * (7-distance) * num_pawns)

	def test_get_open_file_to_king_penalty(self):
		board = chess.Board("3r2k1/p1r5/8/8/8/8/8/K4R2 w - - 0 1")
		color = chess.WHITE
		self.assertEqual(position_evaluator.get_open_file_to_king_penalty(board, color), \
			position_evaluator.HALF_OPEN_FILE_TO_KING_PENALTY + position_evaluator.OPEN_ADJACENT_FILE_TO_KING_PENALTY)

		color = chess.BLACK
		self.assertEqual(position_evaluator.get_open_file_to_king_penalty(board, color), 0)

	def test_repetition_brings_eval_closer_to_zero(self):
		board = chess.Board("rnbqk1nr/p1p5/4ppp1/1p5Q/1bpP4/2N1P3/PP3PPP/R1B1KB1R w KQkq - 0 9")
		turn = chess.WHITE
		evaluation = position_evaluator.evaluate_position(board, turn)
		for move in ["h5g5", "g8h6", "g5h5", "h6g8"]:
			board.push_uci(move)
		self.assertEqual(position_evaluator.evaluate_position(board, turn, check_tactics=True, extend=False), evaluation / 2)

	def test_search_getting_mated(self):
		board = chess.Board("5rk1/p1p1q3/5p1R/2p1p2Q/N7/pP2P3/K1P5/3r4 b - - 6 30")
		turn = chess.BLACK
		self.assertEqual(position_evaluator.search_getting_mated(board, turn), 0)

		# Mate in 2
		board = chess.Board("3r2k1/p1p1q3/5p1R/2p1p2Q/N7/pP2P3/K1P5/3r4 w - - 7 31")
		turn = chess.BLACK
		self.assertEqual(position_evaluator.search_getting_mated(board, turn), position_evaluator.MIN_EVAL + 1)

		# Mate in 1
		board = chess.Board("3r2kR/p1p1q3/5p2/2p1p2Q/N7/pP2P3/K1P5/3r4 b - - 8 31")
		turn = chess.BLACK
		self.assertEqual(position_evaluator.search_getting_mated(board, turn), position_evaluator.MIN_EVAL)

	def test(self):
		turn = chess.WHITE
		board = chess.Board("3r1q1k/1p2r1pb/pnp1B2p/8/P1QP2P1/1PNRPP2/2P2R1P/6K1 b - - 8 36")
		print()
		print("pieces hanging")
		print(position_evaluator.evaluate_position(board, turn))

		#board = chess.Board("1k4r1/2p2p1p/p5Qp/1p2P3/3r1b2/5NP1/PP5P/R1R3K1 b - - 0 23")
		#print()
		#print("trades queen")
		#print(position_evaluator.evaluate_position(board, turn))


if __name__ == '__main__':
	unittest.main()