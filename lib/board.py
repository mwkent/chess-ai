import chess

PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900}
NON_PAWN_PIECE_TYPES = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]

class Board(chess.Board, object):
    def __init__(self, fen=chess.STARTING_FEN, chess960=False):
        self._phase = {chess.WHITE: None, chess.BLACK: None}
        super(Board, self).__init__(fen=fen, chess960=chess960)

    def get_phase(self, color):
        if self._phase[color] == None:
            piece_value_total = 0
            for piece_type in NON_PAWN_PIECE_TYPES:
                pieces = self.pieces(piece_type, not color)
                piece_value_total = piece_value_total + len(pieces) * PIECE_TYPES_TO_VALUES[piece_type]
            # if piece value is greater than or equal to this, then opening
            min_opening_total = 2 * PIECE_TYPES_TO_VALUES[chess.QUEEN]
            # if piece value is less than or equal to this, then endgame
            max_endgame_total = PIECE_TYPES_TO_VALUES[chess.ROOK] + PIECE_TYPES_TO_VALUES[chess.BISHOP]
            scaled_piece_value_total = min(min_opening_total, max(piece_value_total, max_endgame_total)) - max_endgame_total
            scaled_min_opening_total = min_opening_total - max_endgame_total
            self._phase[color] = 1 - (scaled_piece_value_total * 1.0 / scaled_min_opening_total)
        return self._phase[color]
