import unittest
import chess
import minimax
from board import Board

class TestMinimax(unittest.TestCase):

    def test_free_pawn(self):
        board = Board("rnbqkbnr/3ppppp/8/1pp5/PpPP4/8/4PPPP/RNBQKBNR w KQkq - 0 5")
        move = minimax.pick_move(board)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('c4b5'))

    def test_mate_in_3(self):
        board = Board("8/5k2/8/8/8/8/1K1R4/4R3 w - - 2 2")
        move = minimax.pick_move(board, 5)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('d2f2'))

    def test_avoid_mate(self):
        board = Board("r1bqkbnr/1p1np1pp/2P2p2/p7/P2PP3/8/1P3PPP/RNBQKBNR b KQkq - 0 6")
        board.push(chess.Move.from_uci("g7g5"))
        print(board.legal_moves)
        board.pop()
        move = minimax.pick_move(board, depth=2)
        print(move)
        self.assertNotEqual(move, chess.Move.from_uci('g7g5'))

    def test_pin_queen_to_king(self):
        board = Board("2kr2nr/ppp2npp/8/3P4/6qP/4PR2/PP1NK3/R2Q1B2 w - - 0 2")
        move = minimax.pick_move(board)
        print(move)
        self.assertEqual(move, chess.Move.from_uci('f1h3'))


if __name__ == '__main__':
    unittest.main()