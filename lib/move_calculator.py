# Handles calculating which move the engine should play based on a variety of parameters

import time
import minimax_alpha_beta
import position_evaluator

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

    for d in range(1, max_depth + 1):
        print()
        cur_result = minimax_alpha_beta.pick_full_move(board, d)

        elapsed_time = time.time() - start_ts

        result = [cur_result[0], cur_result[1], d, elapsed_time]

        # An estimate on how many times longer it takes to calculate 1 depth deeper than the last
        additional_depth_factor = 10.0
        if (result[0] == position_evaluator.MAX_EVAL) or (result[0] == position_evaluator.MIN_EVAL) or \
            (max_think_time and elapsed_time > max_think_time / additional_depth_factor):
            ponder_move = result
            break

    elapsed_time = time.time() - start_ts

    return result
