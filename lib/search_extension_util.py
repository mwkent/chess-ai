import chess
from typing import List
from board import Board
from constants import MAX_EVAL, MIN_EVAL

"""Utility for search_extension.py and position_evaluator.py
"""

def search_getting_mated_helper(board: Board, turn: chess.Color, num_checks_left: int=2,
                                num_checks_made: int=0) -> (float, List[chess.Move]):
    """Check to see if player is getting mated
    """
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
            search_evaluation = search_getting_mated_helper(
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
                evaluation = search_getting_mated_helper(
                    board, turn, num_checks_left-1, num_checks_made+1)
            board.pop()
            if evaluation[0] != 0:
                return evaluation[0], [move] + evaluation[1]
    return 0, []

def search_getting_mated(board: Board, turn: chess.Color, forced_mate_depth: int=2) -> (float, List[chess.Move]):
    """Does an iterative deepening search
    """
    for num_checks in range(1, forced_mate_depth + 1):
        forced_mate_evaluation = search_getting_mated_helper(board, turn, num_checks_left=num_checks)
        if forced_mate_evaluation[0] != 0:
            return forced_mate_evaluation
    return 0, []

