#! /usr/bin/python

# (C) 2017 by folkert@vanheusden.com
# released under AGPL v3.0

import chess
import chess.pgn
import collections
from log import l
import math
import operator
import sys
import threading
import time
import traceback
import minimax_alpha_beta
import position_evaluator

with_qs = True

to_flag = None

ponder_move = None

def set_to_flag(to_flag):
    to_flag.set()
    l("time is up");

# Can't delete yet
# Returns [move eval, move, depth reached, time taken]
def calc_move_delete(board, max_think_time, max_depth, is_ponder):
    global to_flag
    print("max_think_time =", max_think_time)
    to_flag = threading.Event()
    to_flag.clear()

    t = None
    if max_think_time:
        t = threading.Timer(max_think_time, set_to_flag, args=[to_flag])
        t.start()

    l(board.fen())

    result = None

    start_ts = time.time()
    for d in range(1, max_depth + 1):
        print()
        print("Reached depth of", d)
        cur_result = minimax_alpha_beta.pick_full_move(board, d)

        elapsed_time = time.time() - start_ts

        if to_flag.is_set():
            if result:
                result[3] = elapsed_time
            break

        if cur_result[1]:
            diff_ts_ms = math.ceil(elapsed_time * 1000.0)

        result = [cur_result[0], cur_result[1], d, elapsed_time]

        # An estimate on how much longer it takes to calculate 1 depth deeper than the last
        additional_depth_factor = 10.0
        if (result[0] == position_evaluator.MAX_EVAL) or (max_think_time and elapsed_time > max_think_time / additional_depth_factor):
            break

    if t:
        t.cancel()

    l('selected move: %s' % result)

    elapsed_time = time.time() - start_ts

    return result

# No threading involved
# Returns [move eval, move, depth reached, time taken]
# Todo: Implement ponder
def calc_move_no_thread(board, max_think_time, max_depth, is_ponder):
    global ponder_move
    if is_ponder:
        ponder_move = None
    print("max_think_time =", max_think_time)
    result = None
    start_ts = time.time()

    # If there's only one move, no need to calculate
    moves = list(board.legal_moves) 
    if len(moves) == 1:
        return [None, moves[0], 0, 0]

    for d in range(1, max_depth + 1):
        print()
        cur_result = minimax_alpha_beta.pick_full_move(board, d)

        elapsed_time = time.time() - start_ts

        result = [cur_result[0], cur_result[1], d, elapsed_time]

        # An estimate on how much longer it takes to calculate 1 depth deeper than the last
        additional_depth_factor = 10.0
        if (result[0] == position_evaluator.MAX_EVAL) or (result[0] == position_evaluator.MIN_EVAL) or \
            (max_think_time and elapsed_time > max_think_time / additional_depth_factor):
            ponder_move = result
            break

    elapsed_time = time.time() - start_ts

    return result

# Want to use ids function call
# Returns [move eval, move, depth reached, time taken]
def calc_move(board, max_think_time, max_depth, is_ponder):
    global to_flag
    print("max_think_time =", max_think_time)
    to_flag = threading.Event()
    to_flag.clear()

    t = None
    if max_think_time:
        t = threading.Timer(max_think_time, set_to_flag, args=[to_flag])
        t.start()

    l(board.fen())

    result = None

    result = pick_full_move_in_time(board, max_think_time)

    if t:
        t.cancel()

    l('selected move: %s' % result)

    return result

def calc_move_wrapper(board, duration, depth, is_ponder):
    global thread_result

    try:
        thread_result = calc_move_delete(board, duration, depth, is_ponder)

    except Exception as ex:
        l(str(ex))
        l(traceback.format_exc())

        thread_result = None

thread = None
thread_result = None

# calc move thread start
def cm_thread_start(board, duration=None, depth=10, is_ponder=False):
    global thread
    thread = threading.Thread(target=calc_move_wrapper, args=(board,duration,depth,is_ponder,))
    thread.start()

# calc move thread check
def cm_thread_check():
    global thread
    if thread:
        thread.join(0.05)

        return thread.is_alive()
    
    global thread_result
    # Keep going if no result yet
    if not thread_result:
        return True
    return False

# calc move thread stop
def cm_thread_stop():
    global to_flag
    if to_flag:
        set_to_flag(to_flag)

    global thread
    if not thread:
        return None

    thread.join()
    del thread
    thread = None

    global thread_result
    return thread_result
