# Handles calculating which move the engine should play based on a variety of parameters

import time
import threading
import math
import sys
from multiprocessing import Process, Queue
import minimax_alpha_beta
import position_evaluator
from board import Board
import search_extension
from move_filter import is_hard_tactic, is_soft_tactic
from pickle import NONE

# Mate in 10
MAX_MATING_EVAL = position_evaluator.MAX_EVAL - 10
MIN_MATING_EVAL = position_evaluator.MIN_EVAL + 10

ponder_move = None
move_result = None


class AlarmException(Exception):
    pass


def alarmHandler(signum, frame):
    raise AlarmException


def calculate_with_thread(board: Board, max_think_time, max_depth=20, is_ponder=False):
    # Todo: Should this timeout happen around the specific minimax call instead?
    # Timing out this way could lead to a race condition around move_result being updated
    import signal
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
        if move_result is None:
            print("ERROR: Could not find move in", max_think_time, "second(s)")
            move = list(board.legal_moves)[0]
            print("Playing random move =", move.uci())
            result = [None, move, 0, max_think_time]
        else:
            result = move_result
        return result
        

def calculate_with_thread_multiprocessing(board: Board, max_think_time, max_depth=20, is_ponder=False):
    print("Start calculate_with_thread")
    results = Queue()
    p = Process(target=calculate,
                args=(board, max_think_time, results, max_depth, is_ponder))
    p.start()
    p.join(max_think_time)
    if p.is_alive():
        p.terminate()
        p.join()

    result = None
    if results.empty():
        print("ERROR: Could not find move in", max_think_time, "second(s)")
        move = list(board.legal_moves)[0]
        print("Playing random move =", move.uci())
        result = [None, move, 0, max_think_time]
    else:
        result = results.get()
    results.close()
    
    print("end calculate_with_thread")
    return result


def calculate_with_thread2abclkj(board: Board, max_think_time, max_depth=20, is_ponder=False):
    global move_result
    move_result = None
    p = Process(target=calculate,
                args=(board, max_think_time, max_depth, is_ponder))
    p.start()
    p.join(max_think_time)
    if p.is_alive():
        p.terminate()
        p.join()

    
    
    #thread = threading.Thread(target=calculate,
    #                          args=(board, max_think_time, max_depth, is_ponder))
    #thread.start()
    #time.sleep(max_think_time)
    #thread.join()

    if move_result is None:
        print("ERROR: Could not find move in", max_think_time, "second(s)")
        move = list(board.legal_moves)[0]
        print("Playing random move =", move.uci())
        return [None, move, 0, max_think_time]
    return move_result


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

    #result, stop_search = pick_tactics_move(board, max_think_time, start_ts,
    #                                        move_filter=is_hard_tactic)
    result, stop_search = pick_move(board, max_think_time, start_ts, depth=1,
                                    move_filter=is_hard_tactic)
    set_result(result)
    if stop_search:
        return result

    for depth in range(1, max_depth + 1):

        for move_filter in [is_soft_tactic, None]:

            result, stop_search = pick_move(board, max_think_time, start_ts, depth,
                                            move_filter=move_filter)
            set_result(result)
            if stop_search:
                return result

    return result


def pick_tactics_move(board: Board, max_think_time: float, start_ts: float,
                      move_filter):
    print()
    #evaluation, moves = search_extension.search(board, board.turn, return_best=True)
    evaluation, move = minimax_alpha_beta.pick_full_move(board, depth=1,
                                                          move_filter=move_filter)
    # move = None if not moves else moves[0]

    elapsed_time = time.time() - start_ts
    num_moves = len(list(board.legal_moves))

    print("depth = 0")
    print("evaluation =", evaluation)
    #print("moves =", moves)
    print("move time =", elapsed_time)
    print("num moves =", num_moves)

    result = [evaluation, move, 0, elapsed_time]

    # An estimate on how many times longer it takes to calculate 1 depth deeper than the last
    # additional_depth_factor = 5.0
    # additional_depth_factor = 50.0
    # additional_depth_factor = 100.0
    additional_depth_factor = num_moves * num_moves
    stop_search = result[1] is not None and \
        (is_mating(result[0]) or
         (max_think_time and elapsed_time > max_think_time / additional_depth_factor))

    return result, stop_search


def pick_move(board: Board, max_think_time: float, start_ts: float, depth: int,
              forced_mate_depth: int=2, capture_depth: int=8,
              move_filter=None):
    print()
    cur_result = minimax_alpha_beta.pick_full_move(board, depth,
                                                   forced_mate_depth=forced_mate_depth,
                                                   num_captures=capture_depth,
                                                   move_filter=move_filter)

    elapsed_time = time.time() - start_ts

    result = [cur_result[0], cur_result[1], depth, elapsed_time]

    # An estimate on how many times longer it takes to calculate 1 depth deeper than the last
    additional_depth_factor = 5.0
    # additional_depth_factor = 50.0
    # additional_depth_factor = 100.0
    stop_search = is_mating(result[0]) or \
        (max_think_time and elapsed_time > max_think_time / additional_depth_factor)

    return result, stop_search


def is_mating(evaluation: int) -> bool:
    return evaluation is not None and \
        (evaluation >= MAX_MATING_EVAL or evaluation <= MIN_MATING_EVAL)


def set_result(result) -> None:
    global move_result
    if result[1] is not None:
        move_result = result
