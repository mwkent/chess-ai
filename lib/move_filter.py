import chess
import chess_util
from typing import List
from board import Board
from constants import LONG_RANGE_PIECE_TYPES, PIECE_TYPES_TO_ROUGH_VALUES, MAX_EVAL, WINNING_EVAL, MIN_EVAL, DRAW_EVAL
import position_evaluator


def is_check(board: Board, move: chess.Move) -> bool:
    return board.gives_check(move)


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


def is_check_capture(board: Board, move: chess.Move) -> bool:
    """Is `move` a check and a capture?
    """
    return board.is_capture(move) and board.gives_check(move)


def is_good_capture(board: Board, move: chess.Move) -> bool:
    """Is `move` likely a good capture.
    Is it a fair trade, taking a hanging piece, or taking a piece of higher value?
    """
    return board.is_capture(move) and (is_equal_value_trade(board, move) or
                                       is_higher_value_trade(board, move) or 
                                       is_hanging_piece_capture(board, move))


def is_capture(board: Board, move: chess.Move) -> bool:
    """Is `move` a capture?
    """
    return board.is_capture(move)


def is_check_fork(board: Board, move: chess.Move) -> bool:
    """Is `move` a check and attacking a hanging piece or piece of higher value
    """
    _, rook_to_square = board.get_castling_rook(move)
    try:
        board.push(move)
        if board.is_check():
            piece = move.to_square if rook_to_square is None else rook_to_square
            if not (chess_util.is_soft_free_to_take(board, piece) or board.is_attacked_by_weaker_piece(piece)) and \
                    (board.get_stronger_pieces_attacked_by(piece) or board.get_hanging_pieces_attacked_by(piece)):
                return True
        return False
    finally:
        board.pop()


def does_opened_piece_make_threat(board: Board, piece_color: chess.Color,
                                  piece_from_square: chess.Square) -> bool:
    """Does the piece that was opened from the last move now make a threat?
    e.g., pawn moved opening bishop's attack on a piece
    """
    for opened_piece in board.attackers(piece_color, piece_from_square):
        if board.piece_type_at(opened_piece) in LONG_RANGE_PIECE_TYPES:
            for square in board.attacks(opened_piece).intersection(
                    chess_util.start_ray(opened_piece, piece_from_square)):
                if board.is_stronger_piece_attacked_by(opened_piece, square) or \
                        board.is_hanging_piece_attacked_by(opened_piece, square):
                    return True
    return False


def make_or_relieve_threat(board: Board, move: chess.Move) -> bool:
    """Does `move` make a threat or reduce the number of threats?
    """
    rook_from_square, rook_to_square = board.get_castling_rook(move)
    piece = move.from_square if rook_from_square is None else rook_from_square
    # If piece is attacked by a weaker piece, consider all moves moving the attacked piece
    if chess_util.can_piece_be_captured_by_weaker_piece(board, piece) or \
        chess_util.can_hanging_piece_be_captured(board, piece):
        return True

    attacked_pieces = board.get_stronger_pieces_attacked_by(piece)
    attacked_pieces.update(board.get_hanging_pieces_attacked_by(piece))

    piece_color = board.color_at(piece)
    try:
        board.push(move)
        piece_from_square = piece
        piece = move.to_square if rook_to_square is None else rook_to_square
        if does_opened_piece_make_threat(board, piece_color, piece_from_square) or \
            board.does_piece_defend_attacked_piece(piece):
            # The last move opened up a piece that is making a threat
            return True

        if chess_util.can_piece_be_captured_by_weaker_piece(board, piece) or \
            chess_util.can_hanging_piece_be_captured(board, piece):
            return False

        attacked_pieces_after_move = board.get_stronger_pieces_attacked_by(piece)
        attacked_pieces_after_move.update(board.get_hanging_pieces_attacked_by(piece))
        return bool(attacked_pieces_after_move - attacked_pieces)

    finally:
        board.pop()


def is_attack_or_defend_higher_valued_pieces(board: Board, move: chess.Move) -> bool:
    """Does `move` change the set of stronger attacked pieces for the piece being moved
    or does `move` save the piece being moved from being attacked by a weaker piece
    """
    #rook_from_square, rook_to_square = board.get_castling_rook(move)
    rook_from_square, _ = board.get_castling_rook(move)
    piece = move.from_square if rook_from_square is None else rook_from_square
    # If piece is attacked by a weaker piece, consider all moves moving the attacked piece
    if chess_util.can_piece_be_captured_by_weaker_piece(board, piece):
        return True
    
    all_pieces = board.get_all_pieces()
    attacked_pieces = set()
    for piece in all_pieces:
        attacked_pieces.update(board.get_stronger_pieces_attacked_by(piece))
    
    board.push(move)
    #piece = move.to_square if rook_to_square is None else rook_to_square
    all_pieces = board.get_all_pieces()
    attacked_pieces_after_move = set()
    for piece in all_pieces:
        attacked_pieces_after_move.update(board.get_stronger_pieces_attacked_by(piece))
    #attacked_pieces_after_move = board.get_stronger_pieces_attacked_by(piece)
    more_enemy_attacked = any(board.color_at(piece) == board.turn for piece in attacked_pieces_after_move - attacked_pieces)
    board.pop()
    
    fewer_own_attacked = any(board.color_at(piece) == board.turn for piece in attacked_pieces - attacked_pieces_after_move)
    return fewer_own_attacked or more_enemy_attacked
    
    #return attacked_pieces != attacked_pieces_after_move


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


def is_drawing(board: Board, move: chess.Move):
    board.push(move)
    drawing = chess_util.is_draw(board)
    board.pop()
    return drawing


def is_hard_tactic(board: Board, move: chess.Move):
    """Does `move` have a high likelihood of being a tactical move?
    Consider all moves when in check, quality capture, and pawn promotions. 
    """
    return board.is_check() or is_good_capture(board, move) or is_pawn_promotion_move(move)


def is_soft_tactic(board: Board, move: chess.Move):
    """Does `move` have some likelihood of being a tactical move?
    Consider all moves when in check, quality capture, and pawn promotions. 
    """
    return board.is_check() or is_check(board, move) or is_capture(board, move) or \
        is_pawn_promotion_move(move) or is_pawn_promotion_search_move(board, move) or \
        make_or_relieve_threat(board, move) or \
        is_drawing(board, move)
        #is_attack_or_defend_higher_valued_pieces(board, move) or \
        

def is_soft_not_hard_tactic(board: Board, move: chess.Move):
    return is_soft_tactic(board, move) and not is_hard_tactic(board, move)


def is_non_tactic(board: Board, move: chess.Move):
    return not is_soft_tactic(board, move)


def is_bad_move(board: Board, move: chess.Move):
    """Is `move` with high certainty a bad move?
    Does it hang a minor or major piece?
    """
    piece = move.from_square
    piece_color = board.color_at(piece)
    if not board.is_check() and board.piece_type_at(piece) in (chess_util.MINOR_PIECES + chess_util.MAJOR_PIECES) and \
            not is_capture(board, move) and not any(attacker for attacker in board.attackers(not piece_color, piece)):
        try:
            board.push(move)
            piece = move.to_square
            if not board.has_defender(piece) and any(attacker for attacker in board.attackers(not piece_color, piece)
                                                     if chess_util.can_piece_capture_no_pin(board, attacker, piece)):
                return True
        finally:
            board.pop()
    return False


def get_soft_tactic_moves(board: Board):
    return [move for move in board.legal_moves if is_soft_tactic(board, move)]


def get_potential_tactics_moves(board: Board) -> List[chess.Move]:
    moves = []
    for move in board.legal_moves:
        if board.is_check() or board.gives_check(move) or is_pawn_promotion_move(move) or \
            is_capture(board, move) or is_attack_or_defend(board, move):
            moves.append(move)
    return moves

