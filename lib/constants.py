import chess

# Extends search with a refined list of moves

MAX_EVAL = 1_000_000
WINNING_EVAL = MAX_EVAL / 2
MIN_EVAL = -MAX_EVAL
DRAW_EVAL = 0

# Mate in 10
MAX_MATING_EVAL = MAX_EVAL - 10
MIN_MATING_EVAL = MIN_EVAL + 10

PIECE_TYPES_TO_ROUGH_VALUES = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300,
                               chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 10_000}

LONG_RANGE_PIECE_TYPES = {chess.BISHOP, chess.ROOK, chess.QUEEN}
