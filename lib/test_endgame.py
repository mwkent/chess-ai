import unittest
import chess
import endgame

class TestEndgame(unittest.TestCase):

	def test_is_endgame(self):
		board = chess.Board("1k6/8/8/8/8/3Q4/2K5/8 w - - 0 1")
		self.assertTrue(endgame.is_endgame(board))

	def test_is_not_endgame(self):
		board = chess.Board()
		self.assertFalse(endgame.is_endgame(board))

	def test_get_strong_color(self):
		board = chess.Board("1k6/8/8/8/8/3Q4/2K5/8 w - - 0 1")
		self.assertEqual(endgame.get_strong_color(board), chess.WHITE)

	def test_push_to_corner(self):
		board = chess.Board("1k6/8/8/8/8/3Q4/2K5/8 w - - 0 1")
		weak_king_square = board.king(chess.BLACK)
		self.assertEqual(endgame.push_to_corner(weak_king_square), (3**2 + 2**2) * endgame.EDGE_EVAL)	

	def test_push_close(self):
		board = chess.Board("1k6/8/8/8/8/3Q4/2K5/8 w - - 0 1")
		weak_king_square = board.king(chess.BLACK)
		strong_king_square = board.king(chess.WHITE)
		self.assertEqual(endgame.push_close(weak_king_square, strong_king_square), -6 * endgame.CLOSE_EVAL)

	def test_is_losing(self):
		board = chess.Board("1k6/8/8/8/8/3Q4/2K5/8 w - - 0 1")
		self.assertTrue(endgame.evaluate_position(board, chess.BLACK) <= -endgame.WINNING_EVAL)

	# king close vs far
	def test_king_far(self):
		close_board = chess.Board("8/8/8/8/2k5/1r4pp/8/K7 b - - 1 176")
		close_eval = endgame.evaluate_position(close_board, chess.BLACK)
		far_board = chess.Board("8/8/8/3k4/8/1r4pp/8/K7 w - - 2 177")
		far_eval = endgame.evaluate_position(far_board, chess.BLACK)
		self.assertTrue(far_eval < close_eval)

	def test_has_pawns(self):
		one_pawn_board = chess.Board("8/8/8/2k1KP2/8/8/8/8 w - - 0 1")
		self.assertTrue(endgame.has_pawns(one_pawn_board, chess.WHITE))
		self.assertFalse(endgame.has_pawns(one_pawn_board, chess.BLACK))

	def test_get_num_moves_to_promote(self):
		pawn = chess.A2
		self.assertEqual(endgame.get_num_moves_to_promote(pawn, chess.WHITE), 5)
		self.assertEqual(endgame.get_num_moves_to_promote(pawn, chess.BLACK), 1)

	def test_get_promotion_square(self):
		pawn = chess.A2
		self.assertEqual(endgame.get_promotion_square(pawn, chess.WHITE), chess.A8)
		self.assertEqual(endgame.get_promotion_square(pawn, chess.BLACK), chess.A1)

	def test_is_pawn_outside_of_square(self):
		board = chess.Board("8/8/8/8/6k1/8/P7/7K w - - 0 1")
		pawn = chess.A2
		self.assertTrue(endgame.is_pawn_outside_of_square(board, pawn), pawn)
		board.push(chess.Move.null())
		self.assertFalse(endgame.is_pawn_outside_of_square(board, pawn), None)

	def test_get_pawn_outside_of_square(self):
		board = chess.Board("8/8/8/8/6k1/8/P7/7K w - - 0 1")
		pawn_color = chess.WHITE
		pawn = chess.A2
		self.assertEqual(endgame.get_pawn_outside_of_square(board, pawn_color), pawn)
		board.push(chess.Move.null())
		self.assertEqual(endgame.get_pawn_outside_of_square(board, pawn_color), None)

	def test_is_endgame_when_pawn_outside_square(self):
		board = chess.Board("8/8/8/8/6k1/8/P7/7K w - - 0 1")
		self.assertTrue(endgame.is_endgame(board))

	def test_evaluate_position_when_pawn_outside_square(self):
		board = chess.Board("8/8/8/8/6k1/8/P7/7K w - - 0 1")
		distance_to_promotion = 6
		self.assertEqual(endgame.evaluate_position(board, chess.WHITE), endgame.WINNING_PAWN_EVAL - distance_to_promotion * endgame.CLOSE_EVAL)

	def test_get_material_value(self):
		board = chess.Board("7k/2p3p1/3n3p/8/8/1K1n4/4r3/8 b - - 2 74")
		material_value = 3 * endgame.PIECE_TYPES_TO_VALUES[chess.PAWN] + 2 * endgame.PIECE_TYPES_TO_VALUES[chess.KNIGHT] + \
			endgame.PIECE_TYPES_TO_VALUES[chess.ROOK]
		self.assertEqual(endgame.get_material_value(board, chess.BLACK), material_value)

	def test_push_close_non_pawns(self):
		board = chess.Board("7k/2p3p1/3n3p/8/8/1K1n4/4r3/8 b - - 2 74")
		close_total = -14 * endgame.CLOSE_EVAL
		weak_king = chess.B3
		self.assertEqual(endgame.push_close_non_pawns(board, weak_king), close_total)

	def test(self):
		board = chess.Board("8/7n/8/2p5/2k3p1/1r5p/K7/8 b - - 7 195")
		print()
		print(board)
		print("after knight move")
		print(endgame.evaluate_position(board, chess.BLACK))

		board = chess.Board("5n2/8/8/2p5/6p1/1rk4p/K7/8 b - - 7 195")
		print()
		print(board)
		print("after best move")
		print(endgame.evaluate_position(board, chess.BLACK))


if __name__ == '__main__':
    unittest.main()