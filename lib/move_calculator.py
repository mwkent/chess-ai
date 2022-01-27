# Handles calculating which move the engine should play based on a variety of parameters

import time
import math
import signal
import chess
import minimax_alpha_beta
import position_evaluator
from board import Board
from constants import MAX_MATING_EVAL, MIN_MATING_EVAL
import search_extension
from move_filter import is_hard_tactic, is_soft_tactic, is_soft_not_hard_tactic, is_non_tactic

ponder_move = None
move_result = None


class AlarmException(Exception):
    pass


def alarmHandler(signum, frame):
    raise AlarmException


def calculate_with_thread(board: Board, max_think_time, max_depth=20, is_ponder=False):
    """Returns (evaluation, move, depth, time)
    """
    # Todo: Should this timeout happen around the specific minimax call instead?
    # Timing out this way could lead to a race condition around move_result being updated
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(math.ceil(max_think_time))
    try:
        global move_result
        move_result = None
        board_copy = board.copy()
        calculate(board_copy, max_think_time, max_depth, is_ponder)
        signal.alarm(0)
    except AlarmException:
        pass
    finally:
        result = None
        if move_result is None or move_result[1] is None:
            print("ERROR: Could not find move in", max_think_time, "second(s)")
            move = list(board.legal_moves)[0]
            print("Playing random move =", move.uci())
            result = [None, move, 0, max_think_time]
        else:
            result = move_result
        return result
        

# No threading involved
# Finds the best move to play according to the chess engine
# Returns [move eval, move, depth reached, time taken]
# Todo: Implement ponder
def calculate(board, max_think_time, max_depth=20, is_ponder=False):
    global ponder_move
    if is_ponder:
        ponder_move = None
    print("max_think_time =", max_think_time)
    start_ts = time.time()

    # If there's only one move, no need to calculate
    moves = list(board.legal_moves)
    if len(moves) == 1:
        result = [None, moves[0], 0, 0]
        set_result(result)
        return result

    #result, stop_search = pick_move(board, max_think_time, start_ts, depth=1,
    #                                move_filter=is_hard_tactic)
    result, stop_search = pick_move(board, max_think_time, start_ts, depth=1,
                                    extend_search=False)
    set_result(result)
    if stop_search:
        return result

    for depth in range(1, max_depth + 1):

        move_filters = [is_soft_tactic, None]
        if depth == 1:
            move_filters = [None]
        for move_filter in move_filters:
        #for move_filter in [is_soft_tactic, None]:
        #for move_filter in [is_soft_tactic, is_non_tactic]:
        #for move_filter in [None]:

            result, stop_search = pick_move(board, max_think_time, start_ts, depth,
                                            move_filter=move_filter)
            set_result(result)
            if stop_search:
                return result

    return result


def pick_move(board: Board, max_think_time: float, start_ts: float, depth: int,
              forced_mate_depth: int=2, capture_depth: int=8,
              move_filter=None, extend_search: bool=True):
    print()
    cur_result = minimax_alpha_beta.pick_full_move(board, depth,
                                                   forced_mate_depth=forced_mate_depth,
                                                   num_captures=capture_depth,
                                                   move_filter=move_filter,
                                                   extend_search=extend_search)

    elapsed_time = time.time() - start_ts

    result = [cur_result[0], cur_result[1], depth, elapsed_time]

    # An estimate on how many times longer it takes to calculate 1 depth deeper than the last
    #additional_depth_factor = 1.0
    #if move_filter == is_non_tactic: # depth level will increase
    #    additional_depth_factor = 5.0
    additional_depth_factor = 5.0
    print("additional_depth_factor =", additional_depth_factor)
    stop_search = is_mating(result[0], depth, move_filter) or \
        (max_think_time and elapsed_time > max_think_time / additional_depth_factor)

    return result, stop_search


def is_mating(evaluation: int, depth: int, move_filter) -> bool:
    return evaluation is not None and \
        ((depth > 1) or (depth == 1 and move_filter is None)) and \
        (evaluation >= MAX_MATING_EVAL or evaluation <= MIN_MATING_EVAL)


def set_result(result) -> None:
    global move_result
    if move_result is None or move_result[1] is None or \
        result[1] is not None and result[1] != chess.Move.null():
        # and \
        #   (result[2] > move_result[2] or
        #   result[0] > move_result[0]):
        move_result = result
    print("move_result =", move_result)
