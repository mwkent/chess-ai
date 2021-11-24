import chess
import chess_util
from typing import List, Tuple
from board import Board
import position_evaluator
from move_position_evaluator import MovePositionEvaluator
import endgame

# Extends search with a refined list of moves

MAX_EVAL = 1_000_000
WINNING_EVAL = MAX_EVAL / 2
MIN_EVAL = -MAX_EVAL
DRAW_EVAL = 0

# Todo: Delete and use chess_util copy
PIECE_TYPES_TO_ROUGH_VALUES = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300,
                               chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 10_000}
PIECE_TYPES_TO_VALUES = position_evaluator.PIECE_TYPES_TO_VALUES.copy()
PIECE_TYPES_TO_VALUES[chess.KING] = 0


def extend_search(board, turn, check_tactics, extend):
    maximizing = board.turn == turn
    min_or_max = max if maximizing else min
    evaluation = float('-inf') if maximizing else float('inf')
    for move in board.legal_moves:
        # print()
        #print("move =", move.uci())
        board.push(move)
        evaluation = min_or_max(evaluation, position_evaluator.evaluate_position(
            board, turn, check_tactics, extend))
        board.pop()
    return evaluation


# Search checks in the position
def extend_checks(board, turn, check_tactics, extend):
    maximizing = board.turn == turn
    min_or_max = max if maximizing else min
    # evaluation should be initialized to evaluation for current position
    evaluation = position_evaluator.evaluate_position(board, turn, check_tactics, extend=False)
    for move in board.legal_moves:
        if board.gives_check(move):
            # print(move.uci())
            board.push(move)
            # if checks are bad, ignore them; if checks are good, update evaluation
            evaluation = min_or_max(evaluation, position_evaluator.evaluate_position(
                board, turn, check_tactics, extend))
            board.pop()
    return evaluation


# Check to see if player is getting mated
def search_getting_mated(board, turn, num_checks_left=2, num_checks_made=0):
    if board.is_checkmate():
        if board.turn == turn:
            return MIN_EVAL + num_checks_made, []
        else:
            return MAX_EVAL - num_checks_made, []
    if num_checks_left == 0:
        return 0, []
    # Search all possible moves when in check
    if board.is_check():
        evaluation = None
        for move in board.legal_moves:
            board.push(move)
            search_evaluation = search_getting_mated(
                board, turn, num_checks_left, num_checks_made)
            board.pop()
            # At least one line does not lead to forced mate
            if search_evaluation[0] == 0:
                return search_evaluation
            if evaluation is None:
                evaluation = search_evaluation
            # A check was intercepted with another check leading to forced mate
            elif evaluation[0] != search_evaluation[0]:
                return 0, []
        return evaluation[0], [move] + evaluation[1]
    else:
        # Search checks
        for move in board.legal_moves:
            evaluation = 0, []
            board.push(move)
            if board.is_check():
                evaluation = search_getting_mated(
                    board, turn, num_checks_left-1, num_checks_made+1)
            board.pop()
            if evaluation[0] != 0:
                return evaluation[0], [move] + evaluation[1]
    return 0, []


def is_pawn_promotion_search_move(board: Board, move: chess.Move) -> bool:
    """Is `move` a passed pawn move?
    """
    from_square = move.from_square
    return board.piece_type_at(from_square) == chess.PAWN \
        and position_evaluator.is_passed_pawn(board, from_square)


def is_pawn_promotion_move(move: chess.Move) -> bool:
    """Is `move` promoting a pawn?
    """
    return move.promotion is not None


def is_equal_value_trade(board: Board, move: chess.Move) -> bool:
    """`move` is taking something of roughly equal value
    """
    if board.is_en_passant(move):
        return True
    from_piece_type = board.piece_type_at(move.from_square)
    to_piece_type = board.piece_type_at(move.to_square)
    if from_piece_type is None or to_piece_type is None:
        return False
    return PIECE_TYPES_TO_ROUGH_VALUES[from_piece_type] == PIECE_TYPES_TO_ROUGH_VALUES[to_piece_type]


def is_higher_value_trade(board: Board, move: chess.Move) -> bool:
    """`move` is taking something of higher value
    """
    from_piece_type = board.piece_type_at(move.from_square)
    to_piece_type = board.piece_type_at(move.to_square)
    if from_piece_type is None or to_piece_type is None:
        return False
    return PIECE_TYPES_TO_ROUGH_VALUES[from_piece_type] < PIECE_TYPES_TO_ROUGH_VALUES[to_piece_type]


def is_hanging_piece_capture(board: Board, move: chess.Move) -> bool:
    """`move` is taking a hanging piece
    Is not considering en passant
    """
    if board.piece_at(move.to_square) is None:
        return False
    return chess_util.is_free_to_take(board, move.to_square)


def is_capture(board: Board, move: chess.Move) -> bool:
    """Is `move` a fair trade, taking a hanging piece, or taking a piece of higher value?
    """
    return board.is_capture(move) and (is_equal_value_trade(board, move) or
                                       is_higher_value_trade(board, move) or 
                                       is_hanging_piece_capture(board, move))


def is_capture2(board: Board, move: chess.Move) -> bool:
    """Is `move` a capture?
    """
    return board.is_capture(move)


def is_attack_or_defend(board: Board, move: chess.Move) -> bool:
    """Does `move` change the set of attacked pieces for the piece being moved
    """
    piece = move.from_square
    attacked_pieces = chess.SquareSet()
    for attacked_square in board.attacks(piece):
        if board.piece_at(attacked_square) is not None:
            attacked_pieces.add(attacked_square)
    board.push(move)
    piece = move.to_square
    attacked_pieces_after_move = chess.SquareSet()
    for attacked_square in board.attacks(piece):
        if board.piece_at(attacked_square) is not None:
            attacked_pieces_after_move.add(attacked_square)
    board.pop()
    return attacked_pieces != attacked_pieces_after_move
    

def is_attack_or_defend3(board: Board, move: chess.Move) -> bool:
    """Does `move` change the set of attacked pieces for the piece being moved
    """
    piece = move.from_square
    attacked_pieces = {attacked_square for attacked_square in board.attacks(piece)
                       if board.piece_at(attacked_square) is not None}
    board.push(move)
    piece = move.to_square
    attacked_pieces_after_move = {attacked_square for attacked_square in board.attacks(piece)
                                  if board.piece_at(attacked_square) is not None}
    board.pop()
    return attacked_pieces != attacked_pieces_after_move
    

def is_attack_or_defend2(board: Board, move: chess.Move) -> bool:
    """Does `move` add to the number of hanging pieces or higher valued attacked pieces
    """
    all_free_to_take = chess_util.get_all_free_to_take(board)
    all_attack_higher_value = chess_util.get_all_attack_higher_value(board)
    board.push(move)
    try:
        all_free_to_take_after_move = chess_util.get_all_free_to_take(board)
        all_attack_higher_value_after_move = chess_util.get_all_attack_higher_value(board)

        enemy = board.turn
        player = not board.turn
        
        enemy_has_more_free_to_take_after_move = \
            len(all_free_to_take[enemy]) < len(all_free_to_take_after_move[enemy]) 
        enemy_has_more_higher_attacked_after_move = \
            len(all_attack_higher_value[enemy]) < len(all_attack_higher_value_after_move[enemy]) 
        player_has_less_free_to_take_after_move = \
            len(all_free_to_take[player]) > len(all_free_to_take_after_move[player])
        player_has_less_higher_attacked_after_move = \
            len(all_attack_higher_value[player]) > len(all_attack_higher_value_after_move[player]) 
        #print("move = {}".format(move.uci()))
        #print("enemy_has_more_free_to_take_after_move = {}".format(enemy_has_more_free_to_take_after_move))
        #print("enemy_has_more_higher_attacked_after_move = {}".format(enemy_has_more_higher_attacked_after_move))
        #print("player_has_less_free_to_take_after_move = {}".format(player_has_less_free_to_take_after_move))
        #print("player_has_less_higher_attacked_after_move = {}".format(player_has_less_higher_attacked_after_move))
        
        if enemy_has_more_free_to_take_after_move or enemy_has_more_higher_attacked_after_move or \
            player_has_less_free_to_take_after_move or player_has_less_higher_attacked_after_move:
            return True
        return False
    finally:
        board.pop()


def get_potential_tactics_moves(board: Board) -> List[chess.Move]:
    moves = []
    for move in board.legal_moves:
        if board.is_check() or board.gives_check(move) or is_pawn_promotion_move(move) or \
            is_capture(board, move) or is_attack_or_defend(board, move):
            moves.append(move)
    return moves


# MVV/LVA (Most Valuable Victim/Least Valuable Attacker) move ordering
# Consider non-captures last
def get_mvv_lva_value(board, move):
    if board.gives_check(move):
        check_value = 1000
        return check_value

    if not board.is_capture(move):
        non_capture_value = -1000
        return non_capture_value

    victim = position_evaluator.get_victim_value(board, move)
    attacker = PIECE_TYPES_TO_VALUES[board.piece_type_at(move.from_square)]
    value = victim - attacker
    return value


def minimax(board: Board, turn: chess.Color, maximizing: bool, return_best: bool,
            move: chess.Move, old_evaluation: int,
            move_position_evaluator: MovePositionEvaluator,
            start_evaluation: int, max_loss: int,
            min_or_max_eval: Tuple[int, List[chess.Move]],
            num_checks_remaining: int=1,
            num_pawn_promotion_remaining: int=0, num_captures_remaining: int=2,
            num_attacks_and_defends_remaining: int=0) \
           -> Tuple[int, List[chess.Move]]:

    # Make move and evaluate
    board.push(move)
    evaluation = search_helper(board, turn, return_best, old_evaluation,
                        move_position_evaluator,
                        start_evaluation, max_loss,
                        num_checks_remaining, num_pawn_promotion_remaining,
                        num_captures_remaining, num_attacks_and_defends_remaining)
    board.pop()
    move_position_evaluator.undo_move()
    
    if (return_best and (min_or_max_eval is None or not min_or_max_eval[1])) or \
        (maximizing and (min_or_max_eval is None or evaluation[0] > min_or_max_eval[0])) or \
        (not maximizing and (min_or_max_eval is None or evaluation[0] < min_or_max_eval[0])):
        min_or_max_eval = evaluation[0], [move] + evaluation[1]
        
    return min_or_max_eval


# Todo: Try ordering moves, mvv, lva - this did not help performance
def search_helper(board: Board, turn: chess.Color,
                  return_best: bool=False,
                  old_evaluation: float=None,
                  move_position_evaluator: MovePositionEvaluator=None,
                  start_evaluation: int=None, max_loss: int=100,
                  num_checks_remaining: int=1,
                  num_pawn_promotion_remaining: int=1, num_captures_remaining: int=8,
                  num_attacks_and_defends_remaining: int=0) \
                  -> Tuple[int, List[chess.Move]]:
    """Returns the evaluation and the list of best moves that were calculated
    """
    min_or_max_eval = None
    if move_position_evaluator is None:
        move_position_evaluator = MovePositionEvaluator(board, turn)
        min_or_max_eval = move_position_evaluator.get_evaluation(), []
    else:
        min_or_max_eval = move_position_evaluator.evaluate_after_move(), []
    # Todo: Check
    # min_or_max_eval = position_evaluator.evaluate_position_after_capture(board, turn, old_evaluation), []
    if start_evaluation is None:
        start_evaluation = min_or_max_eval[0]
    if (turn != board.turn and start_evaluation - min_or_max_eval[0] >= max_loss) or \
        (turn == board.turn and start_evaluation - min_or_max_eval[0] <= max_loss * -1):
        # return min_or_max_eval
        num_checks_remaining, num_pawn_promotion_remaining,
        num_attacks_and_defends_remaining = 0
        num_captures_remaining = min(1, num_captures_remaining)
    
    # Don't end search_helper when either player is in check
    if num_checks_remaining == 0 and num_pawn_promotion_remaining == 0 and \
        num_captures_remaining == 0 and num_attacks_and_defends_remaining == 0 and \
        not board.is_check() or board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material():
        
        #print()
        #print(board.move_stack)
        #print(position_evaluator.evaluate_position(board, turn, extend=False))
        
        # Full evaluation at leaf node
        return min_or_max_eval

    # Todo: Check
    # old_evaluation = min_or_max_eval[0]
    maximizing = board.turn == turn
    if board.is_check():
        # Evaluate all moves when in check, so min_or_max should be reset
        min_or_max_eval = None
        for move in board.legal_moves:
            min_or_max_eval = minimax(board, turn, maximizing, return_best,
                                      move, old_evaluation,
                                      move_position_evaluator,
                                      start_evaluation, max_loss, min_or_max_eval,
                                      num_checks_remaining, num_pawn_promotion_remaining,
                                      num_captures_remaining, num_attacks_and_defends_remaining)
    # Not in check
    else:
        moves = list(board.legal_moves)
        if False:
            moves = sorted(moves, reverse = True, key = lambda move: get_mvv_lva_value(board, move))
        for move in moves:
            if move == chess.Move.from_uci("g1f2") and not board.move_stack:
                x = 1
            # Todo: Check if min_or_max_eval is max or min eval to cut short
            if num_checks_remaining > 0 and board.gives_check(move):
                min_or_max_eval = minimax(board, turn, maximizing, return_best,
                                          move, old_evaluation,
                                          move_position_evaluator,
                                          start_evaluation, max_loss, min_or_max_eval,
                                          num_checks_remaining-1, num_pawn_promotion_remaining,
                                          num_captures_remaining, num_attacks_and_defends_remaining)
            # Decrease num checks as well to reduce searching checks in later layers
            elif num_captures_remaining > 0 and is_capture(board, move):
                min_or_max_eval = minimax(board, turn, maximizing, return_best,
                                          move, old_evaluation,
                                          move_position_evaluator,
                                          start_evaluation, max_loss, min_or_max_eval,
                                          num_checks_remaining-1, num_pawn_promotion_remaining,
                                          num_captures_remaining-1, num_attacks_and_defends_remaining)
            elif num_pawn_promotion_remaining > 0 and is_pawn_promotion_move(move):
                min_or_max_eval = minimax(board, turn, maximizing, return_best,
                                          move, old_evaluation,
                                          move_position_evaluator,
                                          start_evaluation, max_loss, min_or_max_eval,
                                          num_checks_remaining, num_pawn_promotion_remaining-1,
                                          num_captures_remaining, num_attacks_and_defends_remaining)
            elif num_attacks_and_defends_remaining > 0 and is_attack_or_defend(board, move):
                min_or_max_eval = minimax(board, turn, maximizing, return_best,
                                          move, old_evaluation,
                                          move_position_evaluator,
                                          start_evaluation, max_loss, min_or_max_eval,
                                          num_checks_remaining, num_pawn_promotion_remaining,
                                          num_captures_remaining, num_attacks_and_defends_remaining-1)

    return min_or_max_eval


def search(board: Board, turn: chess.Color, return_best: bool=False,
           old_evaluation: float=None,
           move_position_evaluator: MovePositionEvaluator=None,
           start_evaluation: int=None, max_loss: int=100,
           num_checks_remaining: int=0,
           num_pawn_promotion_remaining: int=1, num_captures_remaining: int=8,
           num_attacks_and_defends_remaining: int=0,
           forced_mate_depth: int=2):
    """Returns the evaluation and the list of best moves that were calculated
    """
    if endgame.is_endgame(board):
        return position_evaluator.evaluate_position(board, turn), []
    for num_checks in range(1, forced_mate_depth):
        forced_mate_evaluation = search_getting_mated(board, turn, num_checks_left=num_checks)
        if forced_mate_evaluation[0] != 0:
            return forced_mate_evaluation
    return search_helper(board, turn, return_best,
                         old_evaluation, move_position_evaluator,
                         start_evaluation, max_loss,
                         num_checks_remaining, num_pawn_promotion_remaining,
                         num_captures_remaining, num_attacks_and_defends_remaining)
