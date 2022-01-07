import unittest
import chess
import chess_util
import minimax_alpha_beta
from board import Board
import move_filter
import move_calculator
from uci import position
import position_evaluator
import search_extension

class TestMinimaxAlphaBeta(unittest.TestCase):

	"""Mate related tests
	"""

	def test_avoid_mate(self):
		"""g7g5 blunders mate in 1
		"""
		board = Board("r1bqkbnr/1p1np1pp/2P2p2/p7/P2PP3/8/1P3PPP/RNBQKBNR b KQkq - 0 6")
		move = minimax_alpha_beta.pick_move(board, depth=1)
		self.assertNotEqual(move, chess.Move.from_uci('g7g5'))

	def test_avoid_mate2(self):
		"""c4f7 blunders mate in 2
		"""
		board = Board("1r3r1k/p1ppB1p1/3n2Q1/8/2bp1P2/5R2/P5PP/7K b - - 1 25")
		move = minimax_alpha_beta.pick_move(board, depth=1)
		self.assertNotEqual(move, chess.Move.from_uci('c4f7'))

	def test_getting_mated(self):
		"""Even if the engine is getting mated, it should still return a move.
		"""
		board = Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/4K3 w - - 0 34")
		move = minimax_alpha_beta.pick_move(board)
		self.assertNotEqual(move, None)

	def test_mate_with_rook_and_pawn(self):
		"""Mate with rook and pawn against king
		"""
		board = Board("8/4k3/1R6/5P2/5K2/8/8/8 b - - 51 130")
		num_moves = 0
		while not (chess_util.is_game_over(board)):
			move = minimax_alpha_beta.pick_move_ids(board, 2)
			board.push(move)
			num_moves += 1
		print("num_moves to mate with rook =", num_moves)
		self.assertTrue(board.is_checkmate())

	def test_mate_in_1(self):
		board = Board("8/8/8/p1p5/P7/2k5/6q1/1K6 b - - 3 93")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("g2b2"))

	def test_mate_in_2(self):
		board = Board("r1n2n1k/pp4b1/2p3QN/2Pp4/1P1P2P1/P3r2q/1B6/R4RK1 w - - 2 28")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("f1f8"))		

	"""Non-mate related tests
	"""

	def test_free_pawn(self):
		board = Board("rnbqkbnr/3ppppp/8/1pp5/PpPP4/8/4PPPP/RNBQKBNR w KQkq - 0 5")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci('c4b5'))

	def test_free_knight(self):
		board = Board("r1bqkb1r/ppp1pppp/5P2/8/3p4/2N5/PPP1PPPP/R1BQKB1R b KQkq - 0 6")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci('d4c3'))

	def test_knight_blunder(self):
		board = Board("r3r1k1/2p2p1p/1pn1q1p1/3pp2n/8/2P1PPPP/pRQP2BK/B4R2 b - - 1 27")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("h5g3"))
		
	def test_knight_blunder2(self):
		board = Board("r1b3n1/4k1b1/p1n1p2p/1p1p2p1/3P4/2N1BR2/PPP2PP1/1K1R1B2 w - - 0 20")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("c3d5"))

	def test_pinned_defender(self):
		board = Board("b6k/4rnq1/p2ppN1p/3P4/1P3P1Q/2P3P1/7P/R3R2K w - - 0 48")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("e1e6"))

	# Sacs bishop for pawn, knight is defending but pinned
	def test_bishop_blunder(self):
		board = Board("r1bq1rk1/pp1n1nb1/2p1Q2p/8/P2P4/2N1BN2/1PP2PPP/R4RK1 w - - 1 18")
		move = minimax_alpha_beta.pick_move(board, 1)
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
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("c3d3"))

	# Don't go for draw if winning
	def test_draw_by_rep_depth2(self):
		"""Soft tactic should not skip over drawing move
		"""
		board = Board("4r1k1/1p4p1/2p2p1p/3n4/8/1r3PPP/4p3/R1R1B1K1 b - - 1 37")
		board.push(chess.Move.from_uci("g8h8"))
		board.push(chess.Move.from_uci("a1a2"))
		board.push(chess.Move.from_uci("h8g8"))
		board.push(chess.Move.from_uci("a2a1"))
		board.push(chess.Move.from_uci("g8h8"))
		board.push(chess.Move.from_uci("a1a2"))
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		self.assertNotEqual(move, chess.Move.from_uci("h8g8"))

	# Threat to fork king and undefended knight with queen
	def test_fork_threat(self):
		board = Board("r3kbnr/pN1bq1p1/2p2p2/3p3p/P2Pn3/5N2/1PP1PPPP/R1BQKB1R w KQkq - 1 15")
		# Note: Changed from 2 to 1 with quiescence search
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertIn(move, [chess.Move.from_uci("b7c5"), chess.Move.from_uci("c2c3"), chess.Move.from_uci("c1d2")])

	def test_free_bishop(self):
		board = Board("3r2k1/pp5p/2n1p1p1/2p2P2/P7/2b2N2/1PP2PPP/R5K1 w - - 0 16")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("b2c3"))

	def test_check_to_win_queen(self):
		board = Board("r4rk1/pp2bppp/4b3/2p5/2q1NR2/P3P3/1BQP2PP/5RK1 w - - 0 21")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("e4f6"))

	def test_recapture_bishop(self):
		board = Board("r1bq1rk1/pp2bppp/2npp3/3BP3/3P4/1Q3N2/PP3PPP/RNB2RK1 b - - 0 10")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertIn(move, [chess.Move.from_uci("e6d5"), chess.Move.from_uci("c6a5")])

	def test_counterattack(self):
		board = Board("3r1q1k/1p2r1pb/pnp1B2p/8/P1QP2P1/1PN1PP2/2PR1R1P/6K1 w - - 7 36")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertIn(move, [chess.Move.from_uci("c4b4"), chess.Move.from_uci("c4c5")])

	def test_pin_queen_to_king(self):
		board = Board("1r4r1/1pp2p1p/2nbkp2/pB1q4/P2Pp3/1P2P1P1/3NQP1P/1RR3K1 w - - 1 19")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("b5c4"))		

	def test_losing_pawn_to_en_passant(self):
		board = Board("8/pR4p1/1p2k2p/7P/6P1/2P5/r4PK1/8 b - - 7 39")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("e6f6"))
		
	#@unittest.skip("need to figure out how to handle attacking queens in tactics check")
	def test_queen_pinned_to_mate(self):
		board = Board("2rq3r/pp3kpp/5n2/2bpQ3/8/5B2/PPP2PPP/RN2R1K1 b - - 4 15")
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		self.assertEqual(move, chess.Move.from_uci("h8e8"))

	def test_free_bishop2(self):
		board = Board("r1b1k1r1/pp1n1p1p/2pqp3/3p4/3PnB2/3B1NPP/PPP2P2/R2QR1K1 b q - 2 14")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("d6f4"))

	def test_free_pawn2(self):
		# Bishop is attacking a defended knight and a free pawn
		board = Board("r2r2k1/2p1qp1p/1pn2np1/p1b1p3/8/PP1PN2P/1BPQNPP1/3R2KR b - - 4 20")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("c5a3"))

	def test_avoid_draw(self):
		board = Board("8/2Q4k/8/p1p2r1p/5P2/3P2KP/2P2P2/8 b - - 11 42")
		board.push(chess.Move.from_uci("h7g6"))
		board.push(chess.Move.from_uci("c7b6"))
		board.push(chess.Move.from_uci("g6h7"))
		board.push(chess.Move.from_uci("b6c7"))
		board.push(chess.Move.from_uci("h7g6"))
		board.push(chess.Move.from_uci("c7b6"))
		board.push(chess.Move.from_uci("g6h7"))
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("b6c7"))

	def test_endgame_pawn_push(self):
		board = Board("1n6/1P6/7p/1N2k1p1/5pP1/2K5/8/8 b - - 0 50")
		move = minimax_alpha_beta.pick_move(board, 3)
		self.assertNotEqual(move, chess.Move.from_uci("h6h5"))

	def test_bishop_trapped(self):
		board = Board("rnbqk1nr/pppp1p1p/6p1/7b/8/7P/PPPPPPP1/RNBQKBNR b KQkq - 0 1")
		move = minimax_alpha_beta.pick_move(board, 3, move_filter=move_filter.is_soft_tactic,
										move_filter_depth=2)
		self.assertIn(move, {chess.Move.from_uci("g6g5"), chess.Move.from_uci("f7f5")})

	def test_free_pawn3(self):
		board = Board("8/p7/8/1p5R/r2k1P1P/2p3P1/2K5/8 w - - 0 50")
		move = minimax_alpha_beta.pick_move(board, 3, move_filter=move_filter.is_soft_tactic)
		self.assertEqual(move, chess.Move.from_uci("h5b5"))

	def test_knight_sac(self):
		board = Board("6k1/5p2/1p1r2pp/3p1n2/2p1p2q/1PPnP1b1/KBNPB1R1/3Q4 b - - 1 46")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertNotEqual(move, chess.Move.from_uci("f5e3"))

	def test_save_knight(self):
		board = Board("r1b1kb1r/p2npppp/5n2/q1pP4/1p1PP3/2N2N2/PP1Q1PPP/R1B1KB1R w KQkq - 0 8")
		move = minimax_alpha_beta.pick_move(board, 1, extend_search=False)
		board.push(chess.Move.from_uci("c3d1"))
		turn = chess.WHITE
		print(position_evaluator.evaluate_position(board, turn, check_tactics=True, extend=True))
		self.assertIn(move, {chess.Move.from_uci("c3b1"), chess.Move.from_uci("c3d1"),
							chess.Move.from_uci("c3e2")})

	def test_avoid_fork(self):
		board = Board("r1bq1rk1/ppp1ppbp/2n3p1/3p4/4n3/1P2P1P1/PBPP1PBP/RNQ1K1NR b KQ - 3 8")
		#move = minimax_alpha_beta.pick_move(board, 1, extend_search=False)
		move = move_calculator.calculate_with_thread(board, 20)
		self.assertNotEqual(move, chess.Move.from_uci("c8g4"))

	def test_pin_to_queen(self):
		board = Board("8/3rkp1p/pr2q1p1/Rp1pPn2/3Pb3/1BP5/Q1PBR1PP/6K1 b - - 11 23")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("e6c6"))

	def test_avoid_pawn_fork(self):
		"""Avoid pawn forking knight and bishop
		"""
		board = Board("2b2rk1/3q1nbp/2ppppp1/8/PR1PB2Q/2N1P1P1/1PPN1P1P/6K1 w - - 6 64")
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertNotEqual(move, chess.Move.from_uci("d2c4"))

	def test_save_pawn(self):
		board = Board("6k1/2p1np2/1p1b4/p5p1/8/P1P2P1p/1P2KN2/5N2 b - - 3 52")
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		self.assertEqual(move, chess.Move.from_uci("h3h2"))

	def test_soft_tactic_wont_force_blunder(self):
		"""Null move should be an option even if there are no soft tactic moves
		This test may change if is_soft_tactic expands
		"""
		board = Board("8/2p1nk2/1p6/p4p2/8/P1P5/5N2/5N1K w - - 1 59")
		move = minimax_alpha_beta.pick_move(board, 1, move_filter=move_filter.is_soft_tactic)
		self.assertEqual(move, chess.Move.null())

	def test_save_knight2(self):
		board = Board("r2qkbnr/pppbpp1p/6p1/3pP3/1n3P2/N1PP1Q1P/PP2N1P1/R1B1KB1R b KQkq - 0 10")
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		self.assertEqual(move, chess.Move.from_uci("b4c6"))

	def test_avoid_bishop_trap(self):
		board = Board("rn1qkb1r/2pbn1p1/3ppp2/pp6/3PP2B/1B3N2/PPP1NPPP/R2Q1RK1 w kq - 0 11")
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		self.assertIn(move, {chess.Move.from_uci("a2a3"), chess.Move.from_uci("a2a4"),
							chess.Move.from_uci("e2f4")})

	def test_save_bishop(self):
		board = Board("1n1qkb1r/Q1pbn3/3p1p2/1r4p1/pP1PP2B/5N2/P1P1NPPP/R4RK1 w k - 0 17")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("h4g3"))

	def test_avoid_queen_sac(self):
		"""Avoid losing the queen for nothing
		"""
		board = Board("6k1/5ppp/r7/2p1p3/1p6/p2qP1P1/7P/3RQ1K1 b - - 1 82")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertIn(move, {chess.Move.from_uci("e5e4"), chess.Move.from_uci("c5c4"),
							chess.Move.from_uci("d3d6"), chess.Move.from_uci("a6d6"),
							chess.Move.from_uci("d3d1")})



if __name__ == '__main__':
	unittest.main()