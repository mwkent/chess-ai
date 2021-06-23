# Making any modifications I like here in this file
# Transposition Table for storing chess positions
# Can be used to check if a position has already been evaluated
# Uses chess.Board
import chess
import chess.polyglot
import copy

tt = []
tt_size = 0
# number of values that can be stored at each index in table
tt_sub_size = 8
tt_age = 0

class tt_element(object):
    __slots__ = [ 'hash_', 'score', 'flags', 'depth', 'age', 'move', 'turn' ]

    # hash_ because hash is a keyword
    # flags
    def __init__(self, hash_, score, flags, depth, age, move, turn):
        self.hash_ = hash_
        self.score = score
        self.flags = flags
        self.depth = depth
        self.age = age
        self.move = move
        self.turn = turn

def tt_init(size):
    global tt_size, tt_sub_size, tt
    tt_size = size
    tt = [[tt_element(None, None, None, -1, -1, None, False) for i in range(tt_sub_size)] for i in range(tt_size)]

def tt_inc_age():
    global tt_age
    tt_age += 1

def tt_calc_slot(hash_):
    global tt_size
    return hash_ % tt_size

def tt_store(board, alpha, beta, score, move, depth, turn):
    global tt_sub_size, tt, tt_age

    if score <= alpha:
        flags = 'U' # Upper bound
    elif score >= beta:
        flags = 'L' # Lower bound
    else:
        flags = 'E' # Exact, no alpha beta cutoff

    h = chess.polyglot.zobrist_hash(board)
    idx = tt_calc_slot(h)

    # subarray index
    use_ss = None
    use_ss2 = None
    min_depth = 99999

    for i in range(0, tt_sub_size):
        if tt[idx][i].hash_ == h:
            if tt[idx][i].depth > depth:
                return

            if flags != 'E' and tt[idx][i].depth == depth:
                return

            use_ss = i
            break

        if tt[idx][i].age != tt_age:
            use_ss = i
        elif tt[idx][i].depth < min_depth:
            min_depth = tt[idx][i].depth
            use_ss2 = i

        if not use_ss:
            use_ss = use_ss2

    tt[idx][use_ss] = tt_element(h, score, flags, depth, tt_age, move, turn)

def tt_lookup(board):
    global tt_sub_size, tt

    hash_ = chess.polyglot.zobrist_hash(board)
    idx = tt_calc_slot(hash_)

    for i in range(0, tt_sub_size):
        if tt[idx][i].hash_ == hash_:
            if tt[idx][i].move == None or tt[idx][i].move in board.legal_moves:
                return tt[idx][i]

    return None

# Returns [bool, (score, move)]
def tt_lookup_helper(board, alpha, beta, depth, turn):
    tt_hit = tt_lookup(board)
    if not tt_hit:
        return None

    if tt_hit.turn != turn:
        tt_hit.score = -tt_hit.score
    full_move = (tt_hit.score, tt_hit.move)

    if tt_hit.depth < depth:
        return [ False, full_move ]

    # Todo: what to do with E, L, and U
    if tt_hit.flags == 'E':
        return [ True, full_move ]

    if tt_hit.flags == 'L' and tt_hit.score >= beta:
        return [ True, full_move ]

    if tt_hit.flags == 'U' and tt_hit.score <= alpha:
        return [ True, full_move ]

    return [ False, full_move ]

