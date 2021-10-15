import unittest
import chess
from board import Board
from typing import List
from search_extension import get_potential_tactics_moves, search


class TestSearchExtension(unittest.TestCase):

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

	@unittest.skip("need to figure out attacking pieces")
	def test_search_trap_queen(self):
		board = Board("r4rk1/ppp2ppp/1b1p2b1/8/3nN1Pq/3B3P/PPPB1P2/R2K1Q1R w - - 8 17")
		moves = ["d2g5", "g6e4", "g5h4"]
		print(search(board, chess.WHITE))

	def test_search_free_bishop(self):
		board = Board("r1b1k1r1/pp1n1p1p/2pqp3/3p4/3PnB2/3B1NPP/PPP2P2/R2QR1K1 b q - 2 14")
		move = chess.Move.from_uci("d6f4")
		result = search(board, chess.BLACK)
		self.assertEqual(result[1][0], move)

	def test_winning_queen(self):
		board = Board("r4rk1/pp2bppp/4b3/2p5/2q1NR2/P3P3/1BQP2PP/5RK1 w - - 0 21")
		result = search(board, chess.WHITE)
		move = result[1][0]
		self.assertEqual(move, chess.Move.from_uci("e4f6"))

	def test_capture_free_knight(self):
		board = Board("2qr2k1/1pp2p2/2n3p1/4p3/p2p4/3P2N1/2NBPnB1/1Q4KR w - - 0 67")
		turn = chess.BLACK
		result = search(board, turn,
							num_checks_remaining=1, num_pawn_promotion_remaining=1, num_captures_remaining=2)
		self.assertEqual([chess.Move.from_uci("g1f2")], result[1])

	# Threat to fork king and undefended knight with queen
	def test_fork_threat(self):
		board = Board("r3kbnr/pN1bq1p1/2p2p2/3p3p/P2PnB2/5N2/1PP1PPPP/R2QKB1R b KQkq - 2 15")
		turn = chess.WHITE
		result = search(board, turn,
							num_checks_remaining=1, num_pawn_promotion_remaining=1, num_captures_remaining=8)
		self.assertEqual(chess.Move.from_uci("e7b4"), result[1][0])


if __name__ == '__main__':
	unittest.main()
