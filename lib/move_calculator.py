# Handles calculating which move the engine should play based on a variety of parameters

import time
import minimax_alpha_beta
import position_evaluator
from chess import Board

# Mate in 10
MAX_MATING_EVAL = position_evaluator.MAX_EVAL - 10
MIN_MATING_EVAL = position_evaluator.MIN_EVAL + 10

ponder_move = None


# No threading involved
# Finds the best move to play according to the chess engine
# Returns [move eval, move, depth reached, time taken]
# Todo: Implement ponder
def calculate(board, max_think_time, max_depth=20, is_ponder=False):
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

    for depth in range(1, max_depth + 1):

        capture_depth = 2
        starting_capture_depth = capture_depth
        forced_mate_depth = 2
        for i in range(starting_capture_depth, 9, 2):
            capture_depth = i
            # forced mate check only needs to be done once for a node
            if i > starting_capture_depth:
                forced_mate_depth=0

            result, stop_search = pick_move(board, max_think_time, start_ts, depth,
                                            forced_mate_depth=forced_mate_depth, capture_depth=capture_depth)

            if stop_search:
                return result

    return result


def pick_move(board: Board, max_think_time: float, start_ts: float, depth: int,
              forced_mate_depth: int, capture_depth: int):
    print()
    cur_result = minimax_alpha_beta.pick_full_move(board, depth,
                                                   forced_mate_depth=forced_mate_depth,
                                                   num_captures=capture_depth)

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
    return evaluation >= MAX_MATING_EVAL or evaluation <= MIN_MATING_EVAL
