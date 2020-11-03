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

	def test_free_bishop(self):
		board = chess.Board("rnbqk1nr/ppppbppp/4p3/7Q/3P4/2P1P3/PP3PPP/RNB1KBNR b KQkq - 2 4")
		print(position_evaluator.evaluate_position(board, chess.BLACK))
		board = chess.Board("rnbqk1nr/pppp1ppp/4p3/7Q/3P4/b1P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		print(position_evaluator.evaluate_position(board, chess.WHITE))
		board = chess.Board("rnbqk2r/ppppbppp/4pn2/7Q/3P4/2P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		print(position_evaluator.evaluate_position(board, chess.WHITE))

	def test_no_isolated_pawns(self):
		self.assertEqual(position_evaluator.get_num_isolated_pawns(chess.SquareSet([chess.A2, chess.B2, chess.C2, chess.D4, chess.E2, chess.F2, chess.G2, chess.H2])), 0)		

	def test_isolated_pawns(self):
		self.assertEqual(position_evaluator.get_num_isolated_pawns(chess.SquareSet([chess.A2, chess.C5, chess.D4, chess.D6, chess.F2, chess.H2])), 3)

	def test_pawn_free_to_take(self):
		board = chess.Board("r1bqk2r/ppppbppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 7 5")
		self.assertEqual(position_evaluator.count_free_to_take(board, chess.BLACK), position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN] * position_evaluator.FREE_TO_TAKE_MODIFIER)

	# Black's turn, white's pawn is free to take
	def test_pawn_free_to_take_not_turn(self):
		board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
		self.assertEqual(position_evaluator.count_free_to_take(board, chess.BLACK), position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN] * position_evaluator.FREE_TO_TAKE_NOT_TURN_MODIFIER)

	def test_bishop_free_to_take(self):
		board = chess.Board("rnbqk1nr/pppp1ppp/4p3/7Q/3P4/b1P1P3/PP3PPP/RNB1KBNR w KQkq - 3 5")
		self.assertEqual(position_evaluator.count_free_to_take(board, chess.WHITE), position_evaluator.PIECE_TYPES_TO_VALUES[chess.BISHOP] * position_evaluator.FREE_TO_TAKE_MODIFIER)

	def test_one_passed_pawn(self):
		board = chess.Board("4k3/p6p/8/8/8/8/4P3/2K5 w - - 0 1")
		self.assertEqual(position_evaluator.get_num_passed_pawns(board, chess.WHITE), 1)

	def test_two_passed_pawns(self):
		board = chess.Board("4k3/p6p/8/8/8/8/4P3/2K5 w - - 0 1")
		self.assertEqual(position_evaluator.get_num_passed_pawns(board, chess.BLACK), 2)

	def test_defended_value_of_castled(self):
		board = chess.Board("4k3/8/8/8/8/8/PPP5/1KR5 w - - 0 1")
		self.assertEqual(position_evaluator.get_defended_value(board, chess.WHITE), 4 * position_evaluator.DEFENDED_EVAL)

	def test_king_safety_of_open_king(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n2q2/8/Q7/2P2NK1/P5PP/RN3BR1 b - - 3 13")
		num_checks = 7
		percentage_attacked_adjacent = 3.0 / 8
		self.assertEqual(position_evaluator.get_king_safety(board, chess.WHITE), -num_checks * position_evaluator.POTENTIAL_CHECK_EVAL - percentage_attacked_adjacent * position_evaluator.ATTACKING_ADJACENT_EVAL)

	def test_king_safety_of_safe_king(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n2q2/8/Q7/2P2NK1/P5PP/RN3BR1 b - - 3 13")
		num_checks = 0
		percentage_attacked_adjacent = 0.0 / 8
		self.assertEqual(position_evaluator.get_king_safety(board, chess.BLACK), -num_checks * position_evaluator.POTENTIAL_CHECK_EVAL - percentage_attacked_adjacent * position_evaluator.ATTACKING_ADJACENT_EVAL)

	def test_king_safety_of_king_in_check(self):
		board = chess.Board("r1b2rk1/pppp1ppp/2n3q1/8/Q7/2P2NK1/P5PP/RN3BR1 w - - 4 14")
		num_checks = 1
		percentage_attacked_adjacent = 1.0 / 8
		print("num checks =", position_evaluator.get_num_checks(board, chess.WHITE))
		self.assertEqual(position_evaluator.get_king_safety(board, chess.WHITE), -num_checks * position_evaluator.POTENTIAL_CHECK_EVAL - percentage_attacked_adjacent * position_evaluator.ATTACKING_ADJACENT_EVAL)

	def test_center_pawn_eval(self):
		center_pawn_eval = position_evaluator.CENTRAL_PAWN_EVAL * 8
		pawn_squares = chess.SquareSet([chess.A2, chess.B3, chess.C5, chess.D7, chess.F2])
		self.assertEqual(position_evaluator.get_center_pawn_eval(pawn_squares), center_pawn_eval)

	def test_rank_pawn_eval_for_white(self):
		rank_pawn_eval = position_evaluator.RANK_PAWN_EVAL * 9
		pawn_squares = chess.SquareSet([chess.A2, chess.B3, chess.C5, chess.D7, chess.F2])
		self.assertEqual(position_evaluator.get_rank_pawn_eval(pawn_squares, chess.WHITE), rank_pawn_eval)

	def test_rank_pawn_eval_for_black(self):
		rank_pawn_eval = position_evaluator.RANK_PAWN_EVAL * 16
		pawn_squares = chess.SquareSet([chess.A2, chess.B3, chess.C5, chess.D7, chess.F2])
		self.assertEqual(position_evaluator.get_rank_pawn_eval(pawn_squares, chess.BLACK), rank_pawn_eval)

	def test_knight_rank_eval_for_white(self):
		knight_rank_eval = position_evaluator.KNIGHT_RANK_EVAL[4] + position_evaluator.KNIGHT_RANK_EVAL[6]
		knight_squares = chess.SquareSet([chess.C5, chess.D7])
		self.assertEqual(position_evaluator.get_knight_rank_eval(knight_squares, chess.WHITE), knight_rank_eval)

	def test_knight_rank_eval_for_black(self):
		knight_rank_eval = position_evaluator.KNIGHT_RANK_EVAL[3] + position_evaluator.KNIGHT_RANK_EVAL[1]
		knight_squares = chess.SquareSet([chess.C5, chess.D7])
		self.assertEqual(position_evaluator.get_knight_rank_eval(knight_squares, chess.BLACK), knight_rank_eval)

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


if __name__ == '__main__':
    unittest.main()