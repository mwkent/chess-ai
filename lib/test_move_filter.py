import unittest
import chess
from board import Board
from typing import List
from move_filter import get_potential_tactics_moves
import move_filter


class TestMoveFilter(unittest.TestCase):

	def get_potential_tactics_moves_helper(self, board: Board, moves: List[str]):
		# print()
		for move_str in moves:
			# print(get_potential_tactics_moves(board))
			move = chess.Move.from_uci(move_str)
			self.assertIn(move, get_potential_tactics_moves(board))
			board.push(move)
			

	def test_get_potential_tactics_moves_forced_mate(self):
		board = Board("3b2k1/1P5p/2Bp4/3Pp3/5p2/1Q6/P6P/1q4BK b - - 2 41")
		moves = ["b1e4", "b3f3", "e4f3"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_forced_mate2(self):
		board = Board("4r1k1/ppp2p1p/4q1pB/5r2/8/1P1P4/R1PQ1RPP/6K1 b - - 0 22")
		moves = ["e6e1", "d2e1", "e8e1", "f2f1", "e1f1"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_take_queen(self):
		board = Board("1r3r1k/3R3p/p7/1p6/2b2p1P/P1Nq4/1PQ3P1/6K1 w - - 6 44")
		moves = ["d7d3", "c4d3", "c2d3"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_free_knight(self):
		board = Board("r1b2rk1/pp3ppp/5nn1/2Pp2q1/3Pp3/PQ2P2N/4BPPP/R1B2RK1 b - - 1 19")
		moves = ["c8h3"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_win_queen(self):
		board = Board("r4rk1/b2R1ppp/2p3q1/1p2p2n/1PB1P3/2P2Q1P/4NPP1/3R3K w - - 0 24")
		moves = ["c4f7", "g6f7", "d7f7"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_pin_knight(self):
		board = Board("8/8/8/R2p3p/3PbP2/2n3k1/P7/4K3 w - - 0 48")
		moves = ["a5a3", "h5h4", "a3c3"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_sac_then_fork(self):
		board = Board("R7/2kb4/3r3p/2PB2p1/p2K4/5PP1/4P2P/8 b - - 0 36")
		moves = ["d6d5", "d4d5", "d7c6", "d5d4", "c6a8"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_get_potential_tactics_moves_trap_queen(self):
		board = Board("r4rk1/ppp2ppp/1b1p2b1/8/3nN1Pq/3B3P/PPPB1P2/R2K1Q1R w - - 8 17")
		moves = ["d2g5", "g6e4", "g5h4"]
		self.get_potential_tactics_moves_helper(board, moves)

	def test_does_opened_piece_make_threat(self):
		board = Board("rnb1kb1r/pp1p1ppp/q3pn2/2P5/4P3/2P2N2/PP1N1PPP/R1BQKB1R b KQkq - 0 6")
		piece_color = chess.WHITE
		piece_from_square = chess.E2
		self.assertTrue(move_filter.does_opened_piece_make_threat(board, piece_color, piece_from_square))

	def test_make_or_relieve_threat(self):
		board = Board("8/p7/8/1R6/r1k2P1P/2p3P1/2K5/8 w - - 1 51")
		move = chess.Move.from_uci("b5b8")
		self.assertTrue(move_filter.make_or_relieve_threat(board, move))

		move = chess.Move.from_uci("b5a5")
		self.assertTrue(move_filter.make_or_relieve_threat(board, move))

		move = chess.Move.from_uci("f4f5")
		self.assertFalse(move_filter.make_or_relieve_threat(board, move))

	def test_is_attack_or_defend_higher_valued_pieces(self):
		"""Pawn can be moved to attack bishop.
		"""
		board = Board("r1k3br/1pp3pp/p4nn1/5pN1/Nb2p3/1P4B1/P1P1BPPP/R2R2K1 b - - 2 15")
		count = 0
		for move in board.legal_moves:
			count += 1
			print(count, "move =", move, " :",
				move_filter.is_attack_or_defend_higher_valued_pieces(board, move))

		print()
		count = 0
		board = Board("r1k3br/1pp3p1/p4nnp/5pN1/Nb2p3/1P4B1/P1P1BPPP/R2R2K1 w - - 0 16")
		for move in board.legal_moves:
			count += 1
			print(count, "move =", move, " :",
				move_filter.is_attack_or_defend_higher_valued_pieces(board, move))

	def test_is_drawing(self):
		board = Board("4r1k1/1p4p1/2p2p1p/3n4/8/1r3PPP/4p3/R1R1B1K1 b - - 1 37")
		board.push(chess.Move.from_uci("g8h8"))
		board.push(chess.Move.from_uci("a1a2"))
		board.push(chess.Move.from_uci("h8g8"))
		board.push(chess.Move.from_uci("a2a1"))
		board.push(chess.Move.from_uci("g8h8"))
		board.push(chess.Move.from_uci("a1a2"))
		move = chess.Move.from_uci("h8g8")
		self.assertFalse(move_filter.is_drawing(board, move))
		board.push(move)
		self.assertTrue(move_filter.is_drawing(board, chess.Move.from_uci("a2a1")))

	def test_is_soft_tactic(self):
		board = Board("r1k3br/1pp3p1/p4nnp/4P1N1/Nb6/1P4B1/P1P1BPPP/R2R2K1 w - - 0 16")
		moves = ["g5h3", "a4b6", "g3c7", "d1d8", "c2c3", "e5e6"]
		for move_str in moves:
			move = chess.Move.from_uci(move_str)
			self.assertTrue(move_filter.is_soft_tactic(board, move))

	def test_is_soft_tactic2(self):
		board = Board("rnbqk1nr/ppp1ppb1/3p2pp/6B1/2PP4/2N2N2/PP2PPPP/R2QKB1R w KQkq - 4 8")
		move = chess.Move.from_uci("f3e5")
		self.assertFalse(move_filter.is_soft_tactic(board, move))

		board = Board("r2qkbnr/pppb1p1p/4p1p1/3pP3/1n3P2/N1PP1Q1P/PP2N1P1/R1B1KB1R w KQkq - 0 11")
		move = chess.Move.from_uci("c3b4")
		self.assertTrue(move_filter.is_soft_tactic(board, move))

		board = Board("rnb1kb1r/pp1p1ppp/q3pn2/2P5/8/2P2N2/PP1NPPPP/R1BQKB1R w KQkq - 1 6")
		# Opens up attack towards queen
		move = chess.Move.from_uci("e2e4")
		self.assertTrue(move_filter.is_soft_tactic(board, move))

		move = chess.Move.from_uci("b2b4")
		self.assertTrue(move_filter.is_soft_tactic(board, move))

	def test_save_hanging_rook_is_soft_tactic(self):
		board = Board("8/p7/8/1R6/r1k2P1P/2p3P1/2K5/8 w - - 1 51")
		move = chess.Move.from_uci("b5b8")
		self.assertTrue(move_filter.is_soft_tactic(board, move))

	def test_get_soft_tactic_moves(self):
		board = Board("r1k3br/1pp3p1/p4nnp/4P1N1/Nb6/1P4B1/P1P1BPPP/R2R2K1 w - - 0 16")
		print(move_filter.get_soft_tactic_moves(board))

	def test_is_hard_tactic(self):
		"""Pawn is hanging, queens can be traded, and pawn can promote.
		"""
		board = Board("r1bqkb1r/2p3pp/p3Pnn1/5p2/4p3/2N3BN/PpP1BPPP/R2Q1RK1 b kq - 0 10")
		moves = ["c8e6", "d8d1", "b2b1q"]
		for move_str in moves:
			move = chess.Move.from_uci(move_str)
			self.assertTrue(move_filter.is_hard_tactic(board, move))


if __name__ == '__main__':
	unittest.main()
