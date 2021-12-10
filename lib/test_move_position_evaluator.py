import unittest
import chess
import position_evaluator
from move_position_evaluator import MovePositionEvaluator
from board import Board


class TestMovePositionEvaluator(unittest.TestCase):

	def test_capture(self):
		board = Board("rnbqkbnr/1p1ppppp/8/P1p5/1pP5/8/3PPPPP/RNBQKBNR b KQkq - 0 4")
		turn = chess.WHITE
		move = chess.Move.from_uci("a8a5")
		
		evaluator = MovePositionEvaluator(board, turn)
		initial_eval = evaluator.get_evaluation()
		board.push(move)
		eval_after_move = evaluator.evaluate_after_move()

		estimated_value_after_move = initial_eval - position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN]
		# bound on extra value pawn may have had
		error_bound = 50
		self.assertTrue(eval_after_move < estimated_value_after_move + error_bound and
					estimated_value_after_move - error_bound < eval_after_move)

	def test_en_passant_capture(self):
		board = Board("rnbqkbnr/pp1ppppp/8/2pP4/8/8/PPP1PPPP/RNBQKBNR w KQkq c6 0 2")
		turn = chess.WHITE
		move = chess.Move.from_uci("d5c6")
		
		evaluator = MovePositionEvaluator(board, turn)
		initial_eval = evaluator.get_evaluation()
		board.push(move)
		eval_after_move = evaluator.evaluate_after_move()

		estimated_value_after_move = initial_eval + position_evaluator.PIECE_TYPES_TO_VALUES[chess.PAWN]
		# bound on extra value pawn may have had
		error_bound = 50
		self.assertTrue(eval_after_move < estimated_value_after_move + error_bound and
					estimated_value_after_move - error_bound < eval_after_move)

	def test_pawn_promotion(self):
		board = Board("4k3/3q3P/8/8/8/8/8/4K3 w - - 0 1")
		turn = chess.WHITE
		move = chess.Move.from_uci("h7h8q")
		
		evaluator = MovePositionEvaluator(board, turn)
		initial_eval = evaluator.get_evaluation()
		board.push(move)
		eval_after_move = evaluator.evaluate_after_move()

		min_value_increase = 400
		self.assertTrue(initial_eval + min_value_increase < eval_after_move)

	def test_undo_capture(self):
		board = Board("rnbqkbnr/1p1ppppp/8/P1p5/1pP5/8/3PPPPP/RNBQKBNR b KQkq - 0 4")
		turn = chess.WHITE
		move = chess.Move.from_uci("a8a5")
		
		self.helper_test_undo(board, turn, move)

	def test_undo_pawn_promotion(self):
		board = Board("4k3/3q3P/8/8/8/8/8/4K3 w - - 0 1")
		turn = chess.WHITE
		move = chess.Move.from_uci("h7h8q")
		
		self.helper_test_undo(board, turn, move)

	def helper_test_undo(self, board: Board, turn: chess.Color, move: chess.Move):
		evaluator = MovePositionEvaluator(board, turn)
		initial_eval = evaluator.get_evaluation()
		initial_pieces_evaluation = evaluator.pieces_evaluation
		initial_pieces_to_values = evaluator.pieces_to_values
		board.push(move)
		evaluator.evaluate_after_move()
		evaluator.undo_move()
		eval_after_undo = evaluator.get_evaluation()

		self.assertEqual(initial_eval, eval_after_undo)
		self.assertEqual(initial_pieces_evaluation, evaluator.pieces_evaluation)
		self.assertEqual(initial_pieces_to_values, evaluator.pieces_to_values)

	def test_checkmate(self):
		turn = chess.WHITE

		board = Board("rb2r3/p3k1pp/1n1N1pn1/4p3/P4P2/4B1N1/1PPPP1PP/q1K1RQ2 w - - 1 13")
		evaluator = MovePositionEvaluator(board, turn)
		initial_eval = evaluator.get_evaluation()
		self.assertEqual(initial_eval, position_evaluator.MIN_EVAL)

		board = Board("rb2r3/p3k1pp/1n1N1pn1/4p3/P4P2/4B1N1/qPPPP1PP/2K1RQ2 b - - 0 12")
		evaluator = MovePositionEvaluator(board, turn)
		move = chess.Move.from_uci("a2a1")
		board.push(move)
		eval_after_move = evaluator.evaluate_after_move()
		self.assertEqual(eval_after_move, position_evaluator.MIN_EVAL)

	def test_old_evaluator(self):
		board = Board("rnbqkbnr/1p1ppppp/8/2p5/PpP5/8/3PPPPP/RNBQKBNR w KQkq - 0 4")
		turn = chess.WHITE
		print("regular evaluation =", position_evaluator.evaluate_position(board, turn))
		for _ in range(20):
			move = board.legal_moves.__iter__().__next__()
			board.push(move)
			print("evaluation after {} = {}".format(move.uci(), position_evaluator.evaluate_position(board, turn)))

	def test_new_evaluator(self):
		board = Board("rnbqkbnr/1p1ppppp/8/2p5/PpP5/8/3PPPPP/RNBQKBNR w KQkq - 0 4")
		turn = chess.WHITE
		evaluator = MovePositionEvaluator(board, turn)
		print("all pieces evaluation =", evaluator.get_evaluation())
		for _ in range(20):
			move = board.legal_moves.__iter__().__next__()
			board.push(move)
			print("evaluation after {} = {}".format(move.uci(), evaluator.evaluate_after_move()))


if __name__ == '__main__':
	unittest.main()