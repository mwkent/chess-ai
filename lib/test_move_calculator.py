import unittest
import chess
import move_calculator
import chess_util
from board import Board
import position_evaluator
import move_filter

def get_move(board, time=.5):
		return move_calculator.calculate_with_thread(board, time)[1]

class TestMoveCalculator(unittest.TestCase):

	def test_free_pawn(self):
		board = Board("rnbqkbnr/3ppppp/8/1pp5/PpPP4/8/4PPPP/RNBQKBNR w KQkq - 0 5")
		move = get_move(board)
		self.assertEqual(move, chess.Move.from_uci('c4b5'))

	def test_avoid_mate(self):
		board = Board("r1bqkbnr/1p1np1pp/2P2p2/p7/P2PP3/8/1P3PPP/RNBQKBNR b KQkq - 0 6")
		move = get_move(board)
		self.assertNotEqual(move, chess.Move.from_uci('g7g5'))

	@unittest.skip("Fix this")
	def test_avoid_mate2(self):
		board = Board("rb2rk2/pN4pp/1n1p1pn1/4p3/P4P2/4B1N1/qPPPP1PP/2K1RQ2 w - - 1 12")
		move = get_move(board)
		self.assertIn(move, {chess.Move.from_uci('c2c3'), chess.Move.from_uci('c2c4'),
							chess.Move.from_uci('d2d3'), chess.Move.from_uci('d2d4')})

	def test_getting_mated(self):
		board = Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/4K3 w - - 0 34")
		move = get_move(board)
		self.assertNotEqual(move, None)

	def test_free_knight(self):
		board = Board("r1bqkb1r/ppp1pppp/5P2/8/3p4/2N5/PPP1PPPP/R1BQKB1R b KQkq - 0 6")
		move = get_move(board, 4)
		self.assertEqual(move, chess.Move.from_uci('d4c3'))

	def test_knight_blunder(self):
		board = Board("r3r1k1/2p2p1p/1pn1q1p1/3pp2n/8/2P1PPPP/pRQP2BK/B4R2 b - - 1 27")
		move = get_move(board, time=2)
		self.assertNotEqual(move, chess.Move.from_uci("h5g3"))

	@unittest.skip("Too slow to find move that isn't blunder")
	def test_knight_blunder2(self):
		board = Board("rb1kr3/pp4pp/1n1pqpn1/2p1p3/P4P2/3NB1N1/RPPPP1PP/2K1RQ2 w kq - 1 10")
		move = get_move(board, time=5)
		#self.assertNotEqual(move, chess.Move.from_uci("h5g3"))

	# rook and pawn
	def test_mate_with_rook(self):
		board = Board("8/4k3/1R6/5P2/5K2/8/8/8 b - - 51 130")
		num_moves = 0
		while not (chess_util.is_game_over(board)):
			move = get_move(board)
			board.push(move)
			num_moves += 1
		print("num_moves to mate with rook =", num_moves)
		print(board)
		self.assertTrue(board.is_checkmate())

	def test_pinned_defender(self):
		board = Board("b6k/4rnq1/p2ppN1p/3P4/1P3P1Q/2P3P1/7P/R3R2K w - - 0 48")
		move = get_move(board)
		self.assertNotEqual(move, chess.Move.from_uci("e1e6"))

	# Sacs bishop for pawn, knight is defending but pinned
	def test_bishop_blunder(self):
		board = Board("r1bq1rk1/pp1n1nb1/2p1Q2p/8/P2P4/2N1BN2/1PP2PPP/R4RK1 w - - 1 18")
		move = get_move(board, time=1)
		self.assertNotEqual(move, chess.Move.from_uci("e3h6"))

	# Don't go for draw if winning
	def test_draw_by_rep(self):
		board = Board("r5k1/2p2p2/1p1q2p1/3p3p/4p3/3rP1PN/n1N2P1K/R3Q3 b - - 4 43")
		board.push(chess.Move.from_uci("d3c3"))
		board.push(chess.Move.from_uci("e1d1"))
		board.push(chess.Move.from_uci("c3d3"))
		board.push(chess.Move.from_uci("d1e1"))
		board.push(chess.Move.from_uci("d3c3"))
		board.push(chess.Move.from_uci("e1d1"))
		move = get_move(board)
		self.assertNotEqual(move, chess.Move.from_uci("c3d3"))

	# Threat to fork king and undefended knight with queen
	def test_fork_threat(self):
		board = Board("r3kbnr/pN1bq1p1/2p2p2/3p3p/P2Pn3/5N2/1PP1PPPP/R1BQKB1R w KQkq - 1 15")
		move = get_move(board, time=7)
		self.assertIn(move, [chess.Move.from_uci("b7c5"), chess.Move.from_uci("c2c3"), chess.Move.from_uci("c1d2")])

	def test_free_bishop(self):
		board = Board("3r2k1/pp5p/2n1p1p1/2p2P2/P7/2b2N2/1PP2PPP/R5K1 w - - 0 16")
		move = get_move(board)
		self.assertEqual(move, chess.Move.from_uci("b2c3"))

	def test_check_to_win_queen(self):
		board = Board("r4rk1/pp2bppp/4b3/2p5/2q1NR2/P3P3/1BQP2PP/5RK1 w - - 0 21")
		move = get_move(board)
		self.assertEqual(move, chess.Move.from_uci("e4f6"))

	def test_recapture_bishop(self):
		board = Board("r1bq1rk1/pp2bppp/2npp3/3BP3/3P4/1Q3N2/PP3PPP/RNB2RK1 b - - 0 10")
		move = get_move(board)
		self.assertIn(move, [chess.Move.from_uci("e6d5"), chess.Move.from_uci("c6a5")])

	def test_mate_in_2(self):
		board = Board("r1n2n1k/pp4b1/2p3QN/2Pp4/1P1P2P1/P3r2q/1B6/R4RK1 w - - 2 28")
		move = get_move(board, time=4)
		self.assertEqual(move, chess.Move.from_uci("f1f8"))

	def test_counterattack(self):
		board = Board("3r1q1k/1p2r1pb/pnp1B2p/8/P1QP2P1/1PN1PP2/2PR1R1P/6K1 w - - 7 36")
		move = get_move(board)
		self.assertIn(move, [chess.Move.from_uci("c4b4"), chess.Move.from_uci("c4c5")])

	def test_pin_queen_to_king(self):
		board = Board("1r4r1/1pp2p1p/2nbkp2/pB1q4/P2Pp3/1P2P1P1/3NQP1P/1RR3K1 w - - 1 19")
		move = get_move(board, time=2)
		self.assertEqual(move, chess.Move.from_uci("b5c4"))
		
	def test_is_mating(self):
		self.assertTrue(move_calculator.is_mating(position_evaluator.MAX_EVAL - 5,
					depth=1, move_filter=None))
		self.assertTrue(move_calculator.is_mating(position_evaluator.MIN_EVAL + 5,
					depth=1, move_filter=None))
		self.assertFalse(move_calculator.is_mating(0, depth=1, move_filter=None))
		self.assertFalse(move_calculator.is_mating(position_evaluator.MIN_EVAL + 5,
					depth=1, move_filter=move_filter.is_hard_tactic))
		self.assertTrue(move_calculator.is_mating(position_evaluator.MIN_EVAL + 5,
					depth=2, move_filter=move_filter.is_hard_tactic))

	#@unittest.skip("Used for temporary testing")
	def test(self):
		board = Board("8/2br2kp/4p1p1/3q4/1p6/1P3NP1/5P1P/4R1K1 w - - 1 32")
		time = 25
		#move = move_calculator.calculate(board, time)[1]
		move = move_calculator.calculate_with_thread(board, time)[1]
		print(move)


if __name__ == '__main__':
	unittest.main()
