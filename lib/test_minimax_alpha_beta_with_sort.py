import unittest
import chess
import minimax_alpha_beta
import position_evaluator

class TestMinimaxAlphaBetaWithSort(unittest.TestCase):

    def test_free_pawn(self):
        board = chess.Board("rnbqkbnr/3ppppp/8/1pp5/PpPP4/8/4PPPP/RNBQKBNR w KQkq - 0 5")
        move = minimax_alpha_beta.pick_move_with_sort(board)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('c4b5'))

    def test_mate_in_3(self):
    	board = chess.Board("8/5k2/8/8/8/8/1K1R4/4R3 w - - 2 2")
    	move = minimax_alpha_beta.pick_move_with_sort(board, 5)
    	print(move)
    	self.assertEqual(move, chess.Move.from_uci('d2f2'))

    def test_mate_in_1(self):
        board = chess.Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/5K2 b - - 1 34")
        move = minimax_alpha_beta.pick_move_with_sort(board, 3)
        print(move)
        self.assertIn(move, [chess.Move.from_uci('f5d3'), chess.Move.from_uci('f5h3')])

    def test_avoid_mate(self):
    	board = chess.Board("r1bqkbnr/1p1np1pp/2P2p2/p7/P2PP3/8/1P3PPP/RNBQKBNR b KQkq - 0 6")
    	board.push(chess.Move.from_uci("g7g5"))
    	print(board.legal_moves)
    	board.pop()
    	move = minimax_alpha_beta.pick_move_with_sort(board, depth=2)
    	print(move)
    	self.assertNotEqual(move, chess.Move.from_uci('g7g5'))

    def test_pin_queen_to_king(self):
    	board = chess.Board("2kr2nr/ppp2npp/8/3P4/6qP/4PR2/PP1NK3/R2Q1B2 w - - 0 2")
    	move = minimax_alpha_beta.pick_move_with_sort(board)
    	print(move)
    	self.assertEqual(move, chess.Move.from_uci('f1h3'))

    def test_getting_mated(self):
        board = chess.Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/4K3 w - - 0 34")
        move = minimax_alpha_beta.pick_move_with_sort(board)
        print(move)
        self.assertNotEqual(move, None)

    def test_dont_sack_queen(self):
        board = chess.Board("1r1q1nkb/1bp1rp1p/pp1pp1pP/8/3PP3/N2B1NPQ/PPP1KP2/1R5R w - - 2 20")
        move = minimax_alpha_beta.pick_move_with_sort(board, 1)
        print(move)
        self.assertNotEqual(move, chess.Move.from_uci("h3e6"))

    def test_push_pawn(self):
        board = chess.Board("8/8/8/K3k3/1pPpB3/3P4/8/8 b - - 0 1")
        move = minimax_alpha_beta.pick_move_with_sort(board, 3)
        print(move)
        self.assertEqual(move, chess.Move.from_uci("b4b3"))

    def test_pawn_fork(self):
        board = chess.Board("8/1b6/1p1ppk2/pP5p/P2NPK2/6P1/7P/8 b - - 0 1")
        move = minimax_alpha_beta.pick_move_with_sort(board, 3)
        print(move)
        self.assertEqual(move, chess.Move.from_uci("e6e5"))

    @unittest.skip("performance is too slow, takes ~20 minutes to run")
    def test_checks_then_skewer(self):
        board = chess.Board("2r4k/1b4p1/1p4Bp/8/5R2/7P/P4P2/6K1 b - - 0 1")
        move = minimax_alpha_beta.pick_move_with_sort(board, 6)
        print(move)
        self.assertEqual(move, chess.Move.from_uci("c8c1"))

if __name__ == '__main__':
    unittest.main()