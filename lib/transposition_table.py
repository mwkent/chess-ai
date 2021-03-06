# Transposition Table for storing chess positions
# Can be used to check if a position has already been evaluated
import chess
import chess.polyglot
import copy
from log import l

# (C) 2017 by folkert@vanheusden.com
# released under AGPL v3.0

tt = []
tt_size = 0
# number of values that can be stored at each index in table
tt_sub_size = 8
tt_age = 0

class tt_element(object):
    __slots__ = [ 'hash_', 'score', 'flags', 'depth', 'age', 'move', 'turn' ]

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

    l('Set TT size to %d entries ' % size)
    tt_size = size

    dummy_move = chess.Move(0, 0)

    tt = [[tt_element(None, None, None, -1, -1, None, False) for i in range(tt_sub_size)] for i in range(tt_size)]

def tt_inc_age():
    global tt_age

    tt_age += 1

def tt_calc_slot(h):
    global tt_size

    return h % tt_size

def tt_store(board, alpha, beta, score, move, depth, turn):
    global tt_sub_size, tt, tt_age

    if score <= alpha:
        flags = 'U'
    elif score >= beta:
        flags = 'L'
    else:
        flags = 'E' # Exact, no alpha beta cutoff

    h = board.get_zh()
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

    h = board.get_zh()
    idx = tt_calc_slot(h)

    for i in range(0, tt_sub_size):
        if tt[idx][i].hash_ == h:
            if tt[idx][i].move == None or tt[idx][i].move in board.get_move_list():
                return tt[idx][i]

    return None

def tt_lookup_helper(board, alpha, beta, depth, turn):
	tt_hit = tt_lookup(board)
	if not tt_hit:
		return None

	if tt_hit.turn != turn:
		tt_hit.score = -tt_hit.score
	full_move = (tt_hit.score, tt_hit.move)

	if tt_hit.depth < depth:
		return [ False, full_move ]

	if tt_hit.flags == 'E':
		return [ True, full_move ]

	if tt_hit.flags == 'L' and tt_hit.score >= beta:
		return [ True, full_move ]

	if tt_hit.flags == 'U' and tt_hit.score <= alpha:
		return [ True, full_move ]

	return [ False, full_move ]

def tt_get_pv(b, first_move):
    pv = first_move.uci()

    board = b.copy()
    board.push(first_move)

    hist = set()

    while True:
        hit = tt_lookup(board)
        if not hit or not hit.move:
            break

        if hit.move in hist:
            break

        pv += ' ' + hit.move.uci()

        board.push(hit.move)
        hist.add(hit.move)

    return pv
    