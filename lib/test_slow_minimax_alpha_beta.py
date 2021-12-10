import unittest
import chess
import chess_util
import minimax_alpha_beta
from board import Board
import move_filter

# For slower minimax alpha beta tests
class TestSlowMinimaxAlphaBeta(unittest.TestCase):

	# White has mate in 3 moves
	def test_mate_in_3(self):
		board = Board("8/5k2/8/8/8/8/1K1R4/4R3 w - - 2 2")
		move = minimax_alpha_beta.pick_move(board, 5)
		print(move)
		self.assertEqual(move, chess.Move.from_uci('d2f2'))

	# Need to make it so mate in 1 is valued more than mate in 2, etc.
	@unittest.skip("fix")
	def test_mate_in_1(self):
		board = Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/5K2 b - - 1 34")
		move = minimax_alpha_beta.pick_move(board, 3)
		print(move)
		self.assertIn(move, [chess.Move.from_uci('f5d3'), chess.Move.from_uci('f5h3')])

	def test_pin_queen_to_king(self):
		board = Board("2kr2nr/ppp2npp/8/3P4/6qP/4PR2/PP1NK3/R2Q1B2 w - - 0 2")
		move = minimax_alpha_beta.pick_move(board)
		print(move)
		self.assertEqual(move, chess.Move.from_uci('f1h3'))

	def test_take_or_trap_bishop(self):
		board = Board("r5r1/pp1kBpp1/1qppb2p/4p3/5P2/PPQP3P/2P2PB1/R4RK1 b - - 0 18")
		move = minimax_alpha_beta.pick_move(board, 2)
		print("depth = 2:", move)
		self.assertIn(move, [chess.Move.from_uci('d7e7'), chess.Move.from_uci('e5f4')])

	@unittest.skip("missing assert")
	def test_king_blunder(self):
		board = Board("r1bqkb1r/pppp1ppp/1nn1p3/4P3/2PP4/5N2/PP2BPPP/RNBQK2R b KQkq - 1 6")
		print("before move")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		board = Board("r1bq1b1r/ppppkppp/1nn1p3/4P3/2PP4/5N2/PP2BPPP/RNBQK2R w KQ - 2 7")
		print("after blunder")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		board = Board("r1bqkb1r/ppp2ppp/1nnpp3/4P3/2PP4/5N2/PP2BPPP/RNBQK2R w KQkq - 0 7")
		print("after best move")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)

	@unittest.skip("missing assert")
	def test_knight_blunder(self):
		board = Board("4r1k1/pbQ2p1p/8/3p1p2/3P4/2Pq1P2/1r2N1PP/3RR2K b - - 1 23")
		print("depth 1")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		print("depth 2")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		print("depth 3")
		move = minimax_alpha_beta.pick_move(board, 3)
		print(move)
		print("depth 4")
		move = minimax_alpha_beta.pick_move(board, 4)
		print(move)

	@unittest.skip("missing assert")
	def test_rook_fork_blunder(self):
		board = Board("3r4/2p1k3/1p4p1/n1r2pq1/4p2p/4P2R/Q5P1/4BR1K b - - 31 67")
		
		print("depth 1")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		
		print("depth 2")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		
		print("depth 3")
		move = minimax_alpha_beta.pick_move(board, 3)
		print(move)

	# Issue is that there are two pieces hanging
	#@unittest.skip("fix")
	def test_knight_blunder3(self):
		board = Board("rn1qkb1r/1p2nppp/p1pp4/4p3/6b1/4PN2/PPPPBPPP/RNBQ1RK1 w kq - 2 7")
		print("depth 1")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		print("depth 2")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		self.assertNotEqual(move, chess.Move.from_uci("f3e5"))
		print("depth 3")
		move = minimax_alpha_beta.pick_move(board, 3)
		print(move)
		board.push(chess.Move.from_uci("f3e5"))
		print("depth 1 after blunder")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)

	# Does not recognize queen is trapped at depth of 2
	def test_queen_trapped(self):
		board = Board("rnbqkb1r/pp3ppp/2pp1n2/8/B3p3/4PQ2/PPPP1PPP/RNB1K1NR w KQkq - 0 6")
		move = minimax_alpha_beta.pick_move(board, 3)
		self.assertNotEqual(move, chess.Move.from_uci("f3g3"))

	def test_king_rook_fork(self):
		board = Board("r2qkb1r/pp3ppp/3p4/7n/1n2p3/4P2N/PPPP1PPP/RNB1K2R w KQkq - 1 10")
		move = minimax_alpha_beta.pick_move(board, 3)
		self.assertEqual(move, chess.Move.from_uci("b1a3"))

	# Don't develop queen in opening
	# Part of the issue is the queen is pinning pawns for an extra 50 points
	@unittest.skip("figure out how to fix this")
	def test_developing_queen(self):
		board = Board("r1bqkbnr/pppp1ppp/2n5/8/4P3/8/PPP2PPP/RNBQKBNR b KQkq - 2 4")
		print("depth 1")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		print("depth 2")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		#self.assertNotEqual(move, chess.Move.from_uci("f3e5"))
		print("depth 3")
		move = minimax_alpha_beta.pick_move(board, 3)
		print(move)

	# why not move knight out of harms way
	# King safety and pawn value (center pawns and iso) are valuable according to evaluator
	@unittest.skip("figure out how to fix this")
	def test_knight_blunder4(self):
		board = Board("r1b1kb1r/ppp1q1pp/5p2/3pP3/3P2n1/P4N1P/1P3PP1/RNBQK2R b KQkq - 0 11")
		print("depth 1")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		print("depth 2")
		move = minimax_alpha_beta.pick_move(board, 2)
		print(move)
		#self.assertNotEqual(move, chess.Move.from_uci("f3e5"))
		board = Board("r1b1kb1r/ppp1q1pp/5p1n/3pP3/3P4/P4N1P/1P3PP1/RNBQK2R w KQkq - 1 12")
		print("depth 1 after saving knight")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)
		board = Board("r1b1kb1r/ppp1q1pp/8/3pp3/3P2n1/P4N1P/1P3PP1/RNBQK2R w KQkq - 0 12")
		print("depth 1 after taking pawn")
		move = minimax_alpha_beta.pick_move(board, 1)
		print(move)

	# Opponent has forced mate if wrong move is played
	# How to recognize this faster/at lower depths; quiet_search with checks
	# Issue only at depth 2 it seems
	@unittest.skip("missing assert")
	def test_blunders_mate(self):
		board = Board("r2qk2r/2pb4/p1n5/2BN3p/R2Pp2p/1P4P1/2P1PP2/3Q1RK1 w kq - 0 19")
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertNotEqual(move, chess.Move.from_uci("g3h4"))

	# Save bishop instead of castling
	def test_hanging_bishop(self):
		board = Board("r2qk2r/ppp2ppp/2n2n2/3pp3/1b6/2PPP1PP/PP1NBP1R/R1BQK3 b Qkq - 0 9")
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertNotEqual(move, chess.Move.from_uci("e8g8"))

	# Time: 1.9 seconds to run
	# Don't push a knight when it can be easily kicked
	def test_aggressive_knight_push(self):
		board = Board("r1bqkbnr/ppp1n1pp/3p1p2/4p3/3P4/2N1BN2/PPP1PPPP/R2QKB1R w KQkq - 2 6")
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertNotEqual(move, chess.Move.from_uci("c3b5"))

	# Takes ~2 minutes to go to depth 1
	# Delete
	#@unittest.skip("missing assert")
	def test_slow(self):
		board = Board("r1bqkb1r/1pp2pp1/p1np3p/1B2n3/4P3/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 10")
		move = minimax_alpha_beta.pick_move(board, 1)

	# Calculation should be quick when there is only one move available
	# Todo: Delete? Added this functionality in brain.py
	@unittest.skip("figure out how to handle this")
	def test_only_move(self):
		board = Board("rnbqk1nr/pppp1ppp/4p3/8/6Pb/3P1P2/PPP1P2P/RNBQKBNR w KQkq - 0 1")
		minimax_alpha_beta.pick_move(board, 10)		

	# Knight and pawns against bishop
	def test_finish_endgame_quickly(self):
		board = Board("8/8/6p1/4np1p/1k6/p4p2/Bp3K2/8 w - - 0 78")
		num_moves = 0
		while not (chess_util.is_game_over(board)):
			move = minimax_alpha_beta.pick_move_ids(board, 3)
			board.push(move)
			num_moves += 1
		print("num_moves to complete endgame =", num_moves)
		self.assertTrue(board.is_checkmate())
		self.assertTrue(num_moves < 40)

	def test_tactic(self):
		board = Board("1k1r4/pp1Prpp1/2p2n1p/5Q2/8/5N2/qP3PPP/3R2K1 w - - 0 24")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertEqual(move, chess.Move.from_uci("f5f4"))

	def test_skewer_tactic(self):
		board = Board("1r6/1p3R2/p3R3/2k4p/P3PK2/8/8/1r6 w - - 3 37")
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertEqual(move, chess.Move.from_uci("f7c7"))

	def test_move_queen(self):
		board = Board("rbk4r/pp4pp/3p1q2/3p1p2/8/1PBpP3/PK3PPP/R4Q1R b kq - 3 19")
		move = minimax_alpha_beta.pick_move(board, 1)
		self.assertIn(move, {chess.Move.from_uci("f6f7"), chess.Move.from_uci("f6e7"), \
							chess.Move.from_uci("f6g6"), chess.Move.from_uci("d5d4")})
		move = minimax_alpha_beta.pick_move(board, 2)
		self.assertIn(move, {chess.Move.from_uci("f6f7"), chess.Move.from_uci("f6e7"), \
							chess.Move.from_uci("f6g6"), chess.Move.from_uci("d5d4")})

	def test_queen_bishop_hang(self):
		board = Board("rnbqk1nr/ppp1ppb1/3p2pp/6B1/2PP4/2N2N2/PP2PPPP/R2QKB1R w KQkq - 0 6")
		move = minimax_alpha_beta.pick_move(board, 3, move_filter=move_filter.is_soft_tactic,
										move_filter_depth=2)
		self.assertNotEqual(move, chess.Move.from_uci("d1a4"))

	# Winning endgame test
	#@unittest.skip("missing assert")
	def test2(self):
		board = Board("5r2/2bp1pkp/2n3p1/q3P3/1pQ5/1P3N2/5PPP/1N3RK1 w - - 0 26")
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_soft_tactic)
		move = minimax_alpha_beta.pick_move(board, 2, move_filter=move_filter.is_non_tactic)

	def test(self):
		board = Board("1r2r1k1/p1p2ppp/8/1p1p4/4n3/q3PNPP/1nQ1RP2/2B2NK1 b - - 1 24")
		move = minimax_alpha_beta.pick_move(board, 1, extend_search=False)
		move = minimax_alpha_beta.pick_move(board, 1)
		move = minimax_alpha_beta.pick_move(board, 2)



if __name__ == '__main__':
	unittest.main()