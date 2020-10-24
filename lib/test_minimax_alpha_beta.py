import unittest
import chess
import minimax_alpha_beta

class TestMinimaxAlphaBeta(unittest.TestCase):

    def test_free_pawn(self):
        board = chess.Board("rnbqkbnr/3ppppp/8/1pp5/PpPP4/8/4PPPP/RNBQKBNR w KQkq - 0 5")
        move = minimax_alpha_beta.pick_move(board)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('c4b5'))

    def test_mate_in_3(self):
    	board = chess.Board("8/5k2/8/8/8/8/1K1R4/4R3 w - - 2 2")
    	move = minimax_alpha_beta.pick_move(board, 5)
    	print(move)
    	self.assertEqual(move, chess.Move.from_uci('d2f2'))

    def test_mate_in_1(self):
        board = chess.Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/5K2 b - - 1 34")
        move = minimax_alpha_beta.pick_move(board, 3)
        print(move)
        self.assertIn(move, [chess.Move.from_uci('f5d3'), chess.Move.from_uci('f5h3')])

    def test_avoid_mate(self):
    	board = chess.Board("r1bqkbnr/1p1np1pp/2P2p2/p7/P2PP3/8/1P3PPP/RNBQKBNR b KQkq - 0 6")
    	board.push(chess.Move.from_uci("g7g5"))
    	print(board.legal_moves)
    	board.pop()
    	move = minimax_alpha_beta.pick_move(board, depth=2)
    	print(move)
    	self.assertNotEqual(move, chess.Move.from_uci('g7g5'))

    def test_pin_queen_to_king(self):
    	board = chess.Board("2kr2nr/ppp2npp/8/3P4/6qP/4PR2/PP1NK3/R2Q1B2 w - - 0 2")
    	move = minimax_alpha_beta.pick_move(board)
    	print(move)
    	self.assertEqual(move, chess.Move.from_uci('f1h3'))

    def test_getting_mated(self):
        board = chess.Board("1n3k2/5ppr/8/pp1p1b2/3P3P/4rP2/PP5q/4K3 w - - 0 34")
        move = minimax_alpha_beta.pick_move(board)
        print(move)
        self.assertNotEqual(move, None)

    def test_free_knight(self):
        board = chess.Board("r1bqkb1r/ppp1pppp/5P2/8/3p4/2N5/PPP1PPPP/R1BQKB1R b KQkq - 0 6")
        move = minimax_alpha_beta.pick_move(board, 2)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('d4c3'))


if __name__ == '__main__':
    unittest.main()