import chess
from collections import defaultdict
import chess_util
import endgame
from typing import List

# Todo: Knight strength with pawns; knights are stronger in closed positions
# Todo: Avoid exchanges when down material/exchange when up material
# Todo: Escort passed pawn, search queening
# Todo: Weaken queen moves in the opening
# Todo: Issue when both sides have a piece that is free to take. Can we continue the search?
# Todo: Pawn storm
# Todo: Backward pawns
# Todo: Other pins: pin to queen, pin to rook
# Todo: Pressure/attack pinned pieces
# Todo: Skewers
# Todo: Discoveries
# Todo: Reconsider num checks
# Todo: Can bishop be easily kicked
# Todo: How many pieces separate rooks from being connected; discourage rooks getting trapped in the corner
# Todo: Check for type 2 undefended pieces (pieces that are only defended by one piece)
# Todo: Activate king in endgame (needs refinement)
# Todo: Prevent back rank mate and maybe other common mates
# Todo: King pawn endgame
# Todo: Castling - Can still castle, how many pieces preventing castling, which side to castle on
# Todo: King safety - If the king is not in danger, then safe
# Todo: King activation should include infiltration (Refine this)
# Todo: What happens when multiple pieces are free to take? Evaluation is not correct - 2k1r2r/pp5p/2p2p1n/6p1/1P1PBb1N/2P5/P4PPP/R2Q1RK1 b - - 0 24
# Todo: How to evaluate free to take pieces when it is not your turn
# Todo: Bishop or knight close to king helps defend king
# Todo: Measure mobility of pieces to see if a piece could be trapped, check queen mobility
# Todo: It is more important to defend pieces that are attacked, not much value in 2 defenders 0 attackers
# Todo: Search promotion; only pieces or a king can stop a pawn
# Todo: Forks - How to handle multiple pieces attacked
# Todo: Understand pawn breaks

MAX_EVAL = 1_000_000
WINNING_EVAL = MAX_EVAL / 2
MIN_EVAL = -MAX_EVAL
DRAW_EVAL = 0

CENTER = [chess.D4, chess.D5, chess.E4, chess.E5]
SECOND_RING = [chess.C3, chess.C4, chess.C5, chess.C6, chess.D3,
               chess.D6, chess.E3, chess.E6, chess.F3, chess.F4, chess.F5, chess.F6]
THIRD_RING = [chess.B2, chess.B3, chess.B4, chess.B5, chess.B6, chess.B7,
              chess.C2, chess.C7, chess.D2, chess.D7, chess.E2, chess.E7, chess.F2, chess.F7,
              chess.G2, chess.G3, chess.G4, chess.G5, chess.G6, chess.G7]
RIM = [chess.A1, chess.A2, chess.A3, chess.A4, chess.A5, chess.A6, chess.A7, chess.A8,
       chess.B1, chess.B8, chess.C1, chess.C8, chess.D1, chess.D8, chess.E1, chess.E8, chess.F1, chess.F8, chess.G1, chess.G8,
       chess.H1, chess.H2, chess.H3, chess.H4, chess.H5, chess.H6, chess.H7, chess.H8]

# General
ATTACK_VALUE = 2
PRESSURE_PENALTY = -10
FREE_TO_TAKE_MODIFIER = .9
FREE_TO_TAKE_NOT_TURN_MODIFIER = .1
FREE_TO_TAKE_MODIFIER_PENALTY = .1
FREE_TO_TRADE_MODIFIER = 1.1
DEFENDED_EVAL = 7
DOUBLE_DEFENDED_BONUS = 10
DEVELOPMENT_BONUS = [10, 0]

# Pawn
# Todo: Need to figure out what to do with this; needs to be more generic
PAWN_IN_CENTER_EVAL = 10
# Bonus for pawn being closer to the center
CENTRAL_PAWN_EVAL = 3
RANK_PAWN_EVAL = 2
PAWN_RANK_BONUS = [2, 4]
# Delete
ISOLATED_PAWN_EVAL = 30
ISOLATED_PAWN_PENALTY = -30
PASSED_PAWN_EVAL = [30, 60]
PAWN_PROMOTING_RANK_BONUS = [100, 100, 150, 250, 400, 600]
DEFENDING_SQUARE_IN_FRONT_OF_PAWN_BONUS = 10
DEFENDING_TWO_SQUARES_IN_FRONT_OF_PAWN_BONUS = 5
# Bonus for piece being defended by pawn
PAWN_DEFENDING_BONUS = 10
BLOCKADED_PAWN_PENALTY = -5
ROOK_BEHIND_PAWN_BONUS = 15
ROOK_BEHIND_PAWN_PENALTY = -15


# Knight
KNIGHT_RANK_EVAL = [[0, 0], [5, 0], [10, 0], [
    15, 0], [30, 0], [50, 0], [40, 0], [20, 0]]
KICK_KNIGHT_PENALTY = [-30, -10]
KNIGHT_CONTROLLED_PENALTY = -1


# Bishop
PIECE_ON_BISHOP_COLOR_PENALTY = -3
BISHOP_PAIR_EVAL = 20
BISHOP_BATTERY_BONUS = 5
# Long diagonal has some potential
LONG_DIAGONAL_BONUS = [2*ATTACK_VALUE, 0]
BISHOP_BLOCKED_PENALTY = -10


# Knight and Bishop
SQUARES_TO_ATTACKING_BONUS = dict.fromkeys(CENTER, [6, 0])
SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(SECOND_RING, [3, 0]))
SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(THIRD_RING, [1, 0]))
SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(RIM, [0, 0]))

RANKS_TO_ATTACKING_BONUS = dict.fromkeys([0, 1], [0, 0])
RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([2, 3], [1, 0]))
RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([4, 5], [3, 0]))
RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([6, 7], [6, 0]))


# Rook
CONNECTED_ROOKS_EVAL = 10
ROOK_ON_OPEN_FILE_BONUS = [10, 0]
ROOK_ON_HALF_OPEN_FILE_BONUS = [5, 0]
ROOK_TOO_AGGRESSIVE_PENALTY = -10
ROOK_ALIGNED_PENALTY = -15

ROOK_SQUARES_TO_ATTACKING_BONUS = dict.fromkeys(CENTER, [4, 0])
ROOK_SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(SECOND_RING, [2, 0]))
ROOK_SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(THIRD_RING, [1, 0]))
ROOK_SQUARES_TO_ATTACKING_BONUS.update(dict.fromkeys(RIM, [0, 0]))

ROOK_RANKS_TO_ATTACKING_BONUS = dict.fromkeys([0, 1], [0, 0])
ROOK_RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([2, 3], [1, 0]))
ROOK_RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([4, 5], [2, 0]))
ROOK_RANKS_TO_ATTACKING_BONUS.update(dict.fromkeys([6, 7], [4, 0]))


# Queen
QUEEN_ATTACK_VALUE = .2
# The queen being defended is not as important since it only makes a difference if another queen would take it
DEFENDED_QUEEN_BONUS = 1
# If the queen is aligned with the opponent's bishop or rook
QUEEN_ALIGNED_PENALTY = 10


# King
ATTACKING_ADJACENT_EVAL = [100, 0]
SQUARES_TO_WHITE_KING_SAFETY = dict.fromkeys(
    [chess.A1, chess.B1, chess.G1, chess.H1], [30, 0])
SQUARES_TO_WHITE_KING_SAFETY.update(dict.fromkeys(
    [chess.A2, chess.B2, chess.C1, chess.G2, chess.H2], [20, 0]))
SQUARES_TO_BLACK_KING_SAFETY = dict.fromkeys(
    [chess.A8, chess.B8, chess.G8, chess.H8], [30, 0])
SQUARES_TO_BLACK_KING_SAFETY.update(dict.fromkeys(
    [chess.A7, chess.B7, chess.C8, chess.G7, chess.H7], [20, 0]))
CLOSE_PAWN_WALL_EVAL = [20, 0]
FAR_PAWN_WALL_EVAL = [10, 0]
OPEN_FILE_TO_KING_PENALTY = -10
HALF_OPEN_FILE_TO_KING_PENALTY = -5
OPEN_ADJACENT_FILE_TO_KING_PENALTY = -5
HALF_OPEN_ADJACENT_FILE_TO_KING_PENALTY = -2

KING_DISTANCE_TO_PAWN_BONUS = [0, 1]

# Delete
POTENTIAL_CHECK_EVAL = 5
CAN_CASTLE_EVAL = 25
HAS_CASTLED_EVAL = 50


# Todo: Delete and use chess_util copy
PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305,
                         chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900}
PIECE_TYPES_TO_ROUGH_VALUES = {chess.PAWN: 100, chess.KNIGHT: 300,
                               chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900}
NON_PAWN_PIECE_TYPES = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
PIECE_TYPES = [chess.PAWN] + NON_PAWN_PIECE_TYPES
PIECE_TYPES_STRONG_TO_WEAK = [
    chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
ALL_PIECE_TYPES = PIECE_TYPES + [chess.KING]


# returns range between 0 and 1 where 0 is for opening and 1 for endgame
def get_phase(board, color):
    piece_value_total = 0
    for piece_type in NON_PAWN_PIECE_TYPES:
        pieces = board.pieces(piece_type, not color)
        piece_value_total = piece_value_total + \
            len(pieces) * PIECE_TYPES_TO_VALUES[piece_type]
    # if piece value is greater than or equal to this, then opening
    min_opening_total = 2 * PIECE_TYPES_TO_VALUES[chess.QUEEN]
    # if piece value is less than or equal to this, then endgame
    max_endgame_total = PIECE_TYPES_TO_VALUES[chess.ROOK] + \
        PIECE_TYPES_TO_VALUES[chess.BISHOP]
    scaled_piece_value_total = min(min_opening_total, max(
        piece_value_total, max_endgame_total)) - max_endgame_total
    scaled_min_opening_total = min_opening_total - max_endgame_total
    return 1 - (scaled_piece_value_total * 1.0 / scaled_min_opening_total)


def is_endgame(board, color):
    return board.get_phase(color) == 1

# value_range is either a list of two values or a singular value


def get_eval(board, color, value_range):
    value = value_range
    if isinstance(value_range, list):
        phase = board.get_phase(color)
        value_diff = value_range[1] - value_range[0]
        value = phase * value_diff + value_range[0]
    return value

# Gets the bonus for the piece attacking certain squares (e.g. control the center or attack enemy territory)


def get_attacking_bonus(board, color, piece, squares_to_attacking_bonus=SQUARES_TO_ATTACKING_BONUS,
                        ranks_to_attacking_bonus=RANKS_TO_ATTACKING_BONUS):
    bonus = 0
    for attacked_square in board.attacks(piece):
        bonus += get_eval(board, color,
                          squares_to_attacking_bonus.get(attacked_square))
        bonus += get_eval(board, color, ranks_to_attacking_bonus.get(
            chess_util.get_adjusted_rank(attacked_square, color)))
    return bonus

# Is piece being pressured? Is there one attacker and one defender that's not a pawn?
# Pieces are tied down to defending another piece


def get_pressure_penalty(board, piece):
    piece_color = board.color_at(piece)
    attackers = chess_util.get_attackers(board, piece, not piece_color)
    defenders = chess_util.get_attackers(board, piece, piece_color)
    if len(attackers) == 1 and len(defenders) == 1:
        defender = defenders[0]
        if board.piece_type_at(defender) != chess.PAWN:
            return PRESSURE_PENALTY
    return 0

# Are you attacking a defended piece with something of lesser value (i.e. threatening a trade in your favor)
# How to handle attacking piece is also attacked


def attacking_stronger_pieces(board, color, free_to_take=None, free_to_trade=None, free_to_trade_value=0):
    evaluation = 0
    if board.turn != color:
        modifier = FREE_TO_TAKE_NOT_TURN_MODIFIER
        for piece_type in PIECE_TYPES:
            pieces = board.pieces(piece_type, not color)
            for piece in pieces:
                if piece != free_to_take:
                    # attacked by color and defended by not color
                    if board.is_attacked_by(color, piece) and board.is_attacked_by(not color, piece):
                        attackers = board.attackers(color, piece)
                        # difference between attacking piece value and attacked piece value
                        max_difference = 0
                        for attacker in attackers:
                            if board.piece_type_at(attacker) != chess.KING:
                                attacker_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(
                                    attacker)]
                                piece_value = PIECE_TYPES_TO_VALUES[piece_type]
                                if attacker_value < piece_value:
                                    max_difference = max(
                                        max_difference, piece_value - attacker_value)
                        evaluation += max_difference * modifier
    return evaluation

# Delete


def get_num_isolated_pawns(pawns):
    num_isolated_pawns = 0
    pawn_files = list(map(chess.square_file, pawns))
    for pawn_file in pawn_files:
        if pawn_file - 1 not in pawn_files and pawn_file + 1 not in pawn_files:
            num_isolated_pawns += 1
    return num_isolated_pawns


def is_isolated_pawn(pawns, pawn):
    adjacent_files = chess_util.get_adjacent_files(pawn)
    for adjacent_file in adjacent_files:
        if int(pawns) & chess.BB_FILES[adjacent_file]:
            return False
    return True


def get_isolated_pawn_penalty(pawns, pawn):
    return ISOLATED_PAWN_PENALTY if is_isolated_pawn(pawns, pawn) else 0

# Delete? - This was replaced with a check for each pawn instead of all of them


def get_num_passed_pawns(board, turn):
    num_passed_pawns = 0
    own_pawns = board.pieces(chess.PAWN, turn)
    enemy_pawns = board.pieces(chess.PAWN, not turn)
    enemy_pawn_files = list(map(chess.square_file, enemy_pawns))
    # dictionary with default values of empty list
    enemy_pawn_files_to_pawns = defaultdict(list)
    for enemy_pawn in enemy_pawns:
        enemy_pawn_files_to_pawns[chess.square_file(
            enemy_pawn)].append(enemy_pawn)
    for own_pawn in own_pawns:
        own_pawn_file = chess.square_file(own_pawn)
        if own_pawn_file - 1 not in enemy_pawn_files and own_pawn_file not in enemy_pawn_files and own_pawn_file + 1 not in enemy_pawn_files:
            num_passed_pawns += 1
        else:
            own_pawn_rank = chess.square_rank(own_pawn)
            is_passed = True
            for enemy_pawn in (enemy_pawn_files_to_pawns[own_pawn_file - 1] + enemy_pawn_files_to_pawns[own_pawn_file] +
                               enemy_pawn_files_to_pawns[own_pawn_file + 1]):
                if turn:  # White
                    if chess.square_rank(enemy_pawn) > own_pawn_rank:
                        is_passed = False
                        break
                else:  # Black
                    if chess.square_rank(enemy_pawn) < own_pawn_rank:
                        is_passed = False
                        break
            if is_passed:
                num_passed_pawns += 1
    return num_passed_pawns


def is_passed_pawn(board, pawn):
    color = board.color_at(pawn)
    # Squares where an enemy pawn would make pawn not passed
    blocking_squares = chess.SquareSet()
    # Check pawn file as well as adjacent files
    for file_adjust in range(-1, 2):
        adjusted_pawn_square = chess_util.add_file(pawn, file_adjust)
        if adjusted_pawn_square:
            blocking_squares = blocking_squares.union(chess.SquareSet.between(adjusted_pawn_square,
                                                                              endgame.get_promotion_square(adjusted_pawn_square, color)))
    return not any(board.piece_type_at(blocking_square) == chess.PAWN and board.color_at(blocking_square) != color
                   for blocking_square in blocking_squares)

# Pawns closer to the center files are worth more


def get_center_pawn_eval(pawn):
    file_to_center_val = {0: 0, 1: 1, 2: 2, 3: 3, 4: 3, 5: 2, 6: 1, 7: 0}
    return file_to_center_val[chess.square_file(pawn)] * CENTRAL_PAWN_EVAL

# Pawns that are pushed further down the board are worth more


def get_rank_pawn_eval(pawns, turn):
    evaluation = 0
    for pawn in pawns:
        # ranges from 0 to 5
        rank_val = chess.square_rank(pawn) - 1
        max_rank_val = 5
        if (turn == chess.BLACK):
            rank_val = max_rank_val - rank_val
        evaluation += rank_val * RANK_PAWN_EVAL
    return evaluation

# Ranges from 0 to 5 to represent the pawn rank down the board


def get_adjusted_pawn_rank(pawn, color):
    return chess_util.get_adjusted_rank(pawn, color) - 1

# Can the knight catch the pawn before it promotes?
# This function is inexact because returning True does not guarantee the knight can catch the pawn but False guarantees the pawn cannot be caught


def can_knight_catch_pawn(board, knight, pawn):
    pawn_color = board.color_at(pawn)
    color_rank_modifier = 1 if pawn_color else -1
    promotion_rank = 7 if pawn_color else 0
    promotion_file = chess.square_file(pawn)
    pawn_rank = chess.square_rank(pawn)
    knight_rank = chess.square_rank(knight)
    knight_file = chess.square_file(knight)
    file_modifier = 1 if knight_file < promotion_file else -1
    if board.turn == pawn_color:
        pawn_rank += color_rank_modifier
    # +2 because knight gets one time for initial position and one time after pawn promotes
    for _ in range(promotion_rank - pawn_rank + 2):
        rank_diff = abs(promotion_rank - knight_rank)
        file_diff = abs(promotion_file - knight_file)
        if rank_diff == 0 and file_diff == 0:
            return True
        if rank_diff > file_diff:
            knight_rank += color_rank_modifier * min(2, rank_diff)
            knight_file += file_modifier * min(1, file_diff)
        else:
            knight_rank += color_rank_modifier * min(1, rank_diff)
            knight_file += file_modifier * min(2, file_diff)
    return False

# Todo: Check when opponent has knight or bishop as well


def is_pawn_promoting(board, pawn, color):
    promotion_rank = 7
    adjusted_rank = chess_util.get_adjusted_rank(pawn, color)
    if adjusted_rank == promotion_rank - 1 and board.turn == color and not board.is_check() and not board.is_attacked_by(not color, pawn):
        return True
    if not chess_util.has_minor_or_major_pieces(board, not color):
        if endgame.is_pawn_outside_of_square(board, pawn):
            return True
        promotion_square = endgame.get_promotion_square(pawn, color)
        path_to_promote = chess.SquareSet.between(pawn, promotion_square)
        path_to_promote.add(promotion_square)
        if all(board.is_attacked_by(color, square) for square in path_to_promote):
            return True
    if chess_util.has_only_knight_minor_or_major_pieces(board, not color) and \
            all(not can_knight_catch_pawn(board, knight, pawn) for knight in board.pieces(chess.KNIGHT, not color)):
        return True
    return False

# Todo: Each rank should give an extra bonus


def get_pawn_promoting_bonus(board, pawn, color):
    if is_pawn_promoting(board, pawn, color):
        adjusted_pawn_rank = get_adjusted_pawn_rank(pawn, color)
        return PAWN_PROMOTING_RANK_BONUS[adjusted_pawn_rank]
    return 0

# Defend squares in front of pawn


def get_promotion_support_bonus(board, pawn):
    color = board.color_at(pawn)
    modifier = 1 if color == chess.WHITE else -1
    bonus = 0
    next_square = chess_util.add_rank(pawn, modifier)
    if chess_util.are_more_attackers_than_defenders(board, next_square, color):
        bonus += DEFENDING_SQUARE_IN_FRONT_OF_PAWN_BONUS
    next_next_square = chess_util.add_rank(next_square, modifier)
    if next_next_square != None and chess_util.are_more_attackers_than_defenders(board, next_next_square, color):
        bonus += DEFENDING_TWO_SQUARES_IN_FRONT_OF_PAWN_BONUS
    return bonus

# Should be used with passed pawns
# Is there a rook behind or in front of the pawn


def get_rook_behind_pawn_bonus(board, pawn):
    color = board.color_at(pawn)
    value = 0
    rooks = board.pieces(chess.ROOK, color)
    for rook in rooks:
        if chess.square_file(rook) == chess.square_file(pawn) and pawn in board.attacks(rook):
            value += ROOK_BEHIND_PAWN_BONUS
            break
    rooks = board.pieces(chess.ROOK, not color)
    for rook in rooks:
        if chess.square_file(rook) == chess.square_file(pawn) and pawn in board.attacks(rook):
            value += ROOK_BEHIND_PAWN_PENALTY
            break
    return value


def get_blockaded_pawn_penalty(board, pawn):
    color = board.color_at(pawn)
    if (color and board.piece_at(chess_util.add_rank(pawn, 1))) or \
            (not color and board.piece_at(chess_util.add_rank(pawn, -1))):
        return BLOCKADED_PAWN_PENALTY
    return 0

# What makes a pawn stronger or weaker


def get_pawn_value(board, turn, free_to_take):
    evaluation = 0
    pawns = board.pieces(chess.PAWN, turn)
    for pawn in pawns:
        if pawn == free_to_take:
            evaluation += PIECE_TYPES_TO_VALUES[chess.PAWN] * \
                FREE_TO_TAKE_MODIFIER_PENALTY
        else:
            evaluation += PIECE_TYPES_TO_VALUES[chess.PAWN]
            if pawn in CENTER:
                evaluation += PAWN_IN_CENTER_EVAL
            if is_passed_pawn(board, pawn):
                evaluation += get_eval(board, turn, PASSED_PAWN_EVAL)
                evaluation += get_pawn_promoting_bonus(board, pawn, turn)
                evaluation += get_eval(board, turn, PAWN_RANK_BONUS) * \
                    get_adjusted_pawn_rank(pawn, turn) * 2
                evaluation += get_defended_bonus(board, pawn) * 2
                evaluation += get_blockaded_pawn_penalty(board, pawn) * 2
                evaluation += get_rook_behind_pawn_bonus(board, pawn)
                evaluation += get_promotion_support_bonus(board, pawn)
            else:
                evaluation += get_defended_bonus(board, pawn)
                evaluation += get_blockaded_pawn_penalty(board, pawn)
                evaluation += get_eval(board, turn, PAWN_RANK_BONUS) * \
                    get_adjusted_pawn_rank(pawn, turn)
            evaluation += get_center_pawn_eval(pawn)
            evaluation += get_isolated_pawn_penalty(pawns, pawn)
            evaluation += get_pressure_penalty(board, pawn)
    return evaluation

# Returns bonus if piece is not on first rank still


def get_developed_eval(piece, color):
    first_rank = 0
    if chess_util.get_adjusted_rank(piece, color) != first_rank:
        return DEVELOPMENT_BONUS
    return 0


def get_knight_rank_eval(knight, turn):
    # ranges from 0 to 7
    rank_val = chess.square_rank(knight)
    max_rank_val = 7
    if (turn == chess.BLACK):
        rank_val = max_rank_val - rank_val
    return KNIGHT_RANK_EVAL[rank_val]

# The penalty for having a knight on a square where it can easily be kicked by a pawn


def get_kick_knight_penalty(board, knight):
    color = board.color_at(knight)
    color_modifier = 1 if color else -1
    # The rank where a knight can be attacked by a pawn that moves up two squares (0-indexed)
    two_push_knight_rank = 3 if color else 4
    kicker_squares = [chess_util.add_rank_and_file(
        knight, 2*color_modifier, 1), chess_util.add_rank_and_file(knight, 2*color_modifier, -1)]
    if chess.square_rank(knight) == two_push_knight_rank:
        kicker_squares += [chess_util.add_rank_and_file(
            knight, 3*color_modifier, 1), chess_util.add_rank_and_file(knight, 3*color_modifier, -1)]
    for kicker_square in kicker_squares:
        if kicker_square and board.piece_type_at(kicker_square) == chess.PAWN and board.color_at(kicker_square) != color \
                and not board.piece_at(chess_util.add_rank(kicker_square, -1*color_modifier)) \
                and (abs(chess.square_rank(knight) - chess.square_rank(kicker_square)) != 3 or
                     not board.piece_at(chess_util.add_rank(kicker_square, -2*color_modifier))):
            return KICK_KNIGHT_PENALTY
    return 0

# Returns the difference between the knight value and the second highest valuable piece the knight is forking
# i.e. it is assumed the most valuable piece in the fork will move and the knight will be able to trade itself for the second most valuable


def get_knight_fork_value(board, knight):
    all_piece_types_to_values = PIECE_TYPES_TO_VALUES.copy()
    all_piece_types_to_values[chess.KING] = 1000
    knight_color = board.color_at(knight)
    if not chess_util.can_piece_be_captured(board, knight) and not board.is_pinned(knight_color, knight):
        higher_value_attacked_count = 0
        highest_valued_attacked = 0
        second_highest_valued_attacked = 0
        for attacked_piece in board.attacks(knight):
            if board.piece_type_at(attacked_piece) in [chess.ROOK, chess.QUEEN, chess.KING] and board.color_at(attacked_piece) != knight_color:
                value = all_piece_types_to_values[board.piece_type_at(
                    attacked_piece)]
                if value > highest_valued_attacked:
                    second_highest_valued_attacked = highest_valued_attacked
                    highest_valued_attacked = value
                    higher_value_attacked_count += 1
        if higher_value_attacked_count >= 2:  # Knight is forking 2 or more stronger pieces
            return second_highest_valued_attacked - all_piece_types_to_values[chess.KNIGHT]
    return 0

# Are the forward moves for the knight controlled by enemy pawns?


def get_knight_controlled_penalty(board, knight):
    forward_knight_moves = chess_util.get_forward_knight_moves(board, knight)
    knight_color = board.color_at(knight)
    knight_adjusted_rank = chess_util.get_adjusted_rank(knight, knight_color)
    enemy_pawns = board.pieces(chess.PAWN, not knight_color)
    knight_controlled_penalty = 0
    for forward_knight_move in forward_knight_moves:
        if any(forward_knight_move in board.attacks(enemy_pawn) and chess_util.can_piece_capture(board, enemy_pawn, forward_knight_move)
                for enemy_pawn in enemy_pawns):
            knight_controlled_penalty += (chess_util.get_adjusted_rank(forward_knight_move, knight_color) - knight_adjusted_rank) \
                * KNIGHT_CONTROLLED_PENALTY
    return knight_controlled_penalty


# What makes a knight stronger or weaker
def get_knight_value(board, turn, free_to_take, free_to_trade, free_to_trade_value):
    evaluation = 0
    knights = board.pieces(chess.KNIGHT, turn)
    for knight in knights:
        if knight == free_to_take:
            evaluation += PIECE_TYPES_TO_VALUES[chess.KNIGHT] * \
                FREE_TO_TAKE_MODIFIER_PENALTY
        elif knight == free_to_trade:
            evaluation += FREE_TO_TRADE_MODIFIER * free_to_trade_value
        else:
            evaluation += PIECE_TYPES_TO_VALUES[chess.KNIGHT]
            if not board.is_pinned(turn, knight):
                evaluation += len(board.attacks(knight)) * ATTACK_VALUE
                evaluation += get_eval(board, turn,
                                       get_attacking_bonus(board, turn, knight))
            # I don't think this is needed anymore with attacking_bonus
            #value += get_eval(board, turn, get_knight_rank_eval(knight, turn))
            evaluation += get_defended_bonus(board, knight)
            evaluation += get_eval(board, turn,
                                   get_developed_eval(knight, turn))
            evaluation += get_eval(board, turn,
                                   get_kick_knight_penalty(board, knight))
            knight_fork_value = get_knight_fork_value(board, knight)
            evaluation += FREE_TO_TRADE_MODIFIER * knight_fork_value
            evaluation += get_pressure_penalty(board, knight)
    return evaluation

# If the opponent has bishops on only one color complex, is piece on the same color?


def is_piece_on_bishop_color(board, piece):
    bishop_color = not board.color_at(piece)
    bishops = board.pieces(chess.BISHOP, bishop_color)
    return chess_util.on_light_squares(bishops) and not chess_util.on_dark_squares(bishops) and chess_util.is_piece_on_light_square(piece) or \
        chess_util.on_dark_squares(bishops) and not chess_util.on_light_squares(
            bishops) and chess_util.is_piece_on_dark_square(piece)


def get_piece_on_bishop_color_penalty(board, piece):
    return PIECE_ON_BISHOP_COLOR_PENALTY if is_piece_on_bishop_color(board, piece) else 0

# Gives bonus if bishop is in a battery with another bishop or queen of the same color


def get_bishop_battery_bonus(board, bishop, color):
    if any(board.piece_type_at(piece) in [chess.QUEEN, chess.BISHOP] and board.color_at(piece) == color for piece in board.attackers(color, bishop)):
        return BISHOP_BATTERY_BONUS
    return 0


def get_long_diagonal_bonus(bishop):
    long_diagonals = chess.SquareSet.ray(chess.A1, chess.B2).union(
        chess.SquareSet.ray(chess.A8, chess.B7))
    return LONG_DIAGONAL_BONUS if bishop in long_diagonals else 0


def get_bishop_pair_value(bishops):
    if chess_util.on_light_squares(bishops) and chess_util.on_dark_squares(bishops):
        return BISHOP_PAIR_EVAL
    return 0


def get_undeveloped_bishop_blocked_penalty(board, bishop):
    color = board.color_at(bishop)
    if chess_util.get_adjusted_rank(bishop, color) == 0:
        rank_adjustment = 1 if color == chess.WHITE else -1
        blocking_squares = [chess_util.add_rank_and_file(
            bishop, rank_adjustment, 1), chess_util.add_rank_and_file(bishop, rank_adjustment, -1)]
        if all(blocking_square == None or board.color_at(blocking_square) == color for blocking_square in blocking_squares):
            return BISHOP_BLOCKED_PENALTY
    return 0


# What makes a bishop stronger or weaker
def get_bishop_value(board, turn, free_to_take, free_to_trade, free_to_trade_value):
    evaluation = 0
    bishops = board.pieces(chess.BISHOP, turn)
    for bishop in bishops:
        if bishop == free_to_take:
            evaluation += PIECE_TYPES_TO_VALUES[chess.BISHOP] * \
                FREE_TO_TAKE_MODIFIER_PENALTY
        elif bishop == free_to_trade:
            evaluation += FREE_TO_TRADE_MODIFIER * free_to_trade_value
        else:
            evaluation += PIECE_TYPES_TO_VALUES[chess.BISHOP]
            if not chess_util.is_bishop_pinned(board, bishop, turn):
                evaluation += len(board.attacks(bishop)) * ATTACK_VALUE
                evaluation += get_eval(board, turn,
                                       get_attacking_bonus(board, turn, bishop))
                evaluation += get_eval(board, turn,
                                       get_long_diagonal_bonus(bishop))
            evaluation += get_defended_bonus(board, bishop)
            evaluation += get_bishop_battery_bonus(board, bishop, turn)
            evaluation += get_eval(board, turn,
                                   get_developed_eval(bishop, turn))
            evaluation += get_undeveloped_bishop_blocked_penalty(board, bishop)
            evaluation += get_pressure_penalty(board, bishop)
    evaluation += get_bishop_pair_value(bishops)
    return evaluation


def get_connected_rooks_value(board, rooks):
    evaluation = 0
    rooks = list(rooks)
    if len(rooks) == 2 and rooks[0] in board.attacks(rooks[1]):
        evaluation += CONNECTED_ROOKS_EVAL
    return evaluation


def get_rook_on_open_file_bonus(board, rook):
    if chess_util.is_open_file(board, rook):
        return ROOK_ON_OPEN_FILE_BONUS
    if chess_util.is_half_open_file(board, rook):
        return ROOK_ON_HALF_OPEN_FILE_BONUS
    return 0

# A rook extending past the first 3 ranks when the opponent has 3 or more minor pieces becomes a target


def get_rook_too_aggressive_penalty(board, rook):
    rook_color = board.color_at(rook)
    if chess_util.get_adjusted_rank(rook, rook_color) > 2 and chess_util.get_num_minor_pieces(board, not rook_color) > 2:
        return ROOK_TOO_AGGRESSIVE_PENALTY
    return 0

# Is the rook aligned with the opponent's bishop and is there one piece in between


def get_rook_aligned_with_bishop_penalty(board, rook):
    rook_color = board.color_at(rook)
    for diagonal_square in chess_util.get_diagonals(rook):
        if board.piece_type_at(diagonal_square) == chess.BISHOP and board.color_at(diagonal_square) != rook_color:
            num_pieces_in_between = 0
            for in_between_square in chess.SquareSet.between(rook, diagonal_square):
                if board.piece_at(in_between_square):
                    num_pieces_in_between += 1
            if num_pieces_in_between == 1:
                return ROOK_ALIGNED_PENALTY
    return 0


# What makes a rook stronger or weaker
def get_rook_value(board, turn, free_to_take=None, free_to_trade=None, free_to_trade_value=0):
    evaluation = 0
    rooks = board.pieces(chess.ROOK, turn)
    for rook in rooks:
        if rook == free_to_take:
            evaluation += PIECE_TYPES_TO_VALUES[chess.ROOK] * \
                FREE_TO_TAKE_MODIFIER_PENALTY
        elif rook == free_to_trade:
            evaluation += FREE_TO_TRADE_MODIFIER * free_to_trade_value
        elif chess_util.is_rook_pinned(board, rook, turn) and board.piece_type_at(chess_util.get_pinner(board, rook)) == chess.BISHOP:
            evaluation += PIECE_TYPES_TO_VALUES[chess.BISHOP] * \
                FREE_TO_TRADE_MODIFIER
        else:
            evaluation += PIECE_TYPES_TO_VALUES[chess.ROOK]
            if not chess_util.is_rook_pinned(board, rook, turn):
                evaluation += len(board.attacks(rook)) * ATTACK_VALUE
                evaluation += get_eval(board, turn,
                                       get_attacking_bonus(board, turn, rook, ROOK_SQUARES_TO_ATTACKING_BONUS, ROOK_RANKS_TO_ATTACKING_BONUS))
            evaluation += get_defended_bonus(board, rook)
            evaluation += get_eval(board, turn,
                                   get_rook_on_open_file_bonus(board, rook))
            evaluation += get_piece_on_bishop_color_penalty(board, rook)
            evaluation += get_rook_too_aggressive_penalty(board, rook)
            evaluation += get_pressure_penalty(board, rook)
            evaluation += get_rook_aligned_with_bishop_penalty(board, rook)
    evaluation += get_connected_rooks_value(board, rooks)
    return evaluation


# Is the queen aligned with the opponent's bishop or rook and is there one piece in between
def get_queen_aligned_value(board, color):
    value = 0
    queens = board.pieces(chess.QUEEN, color)
    for queen in queens:
        for diagonal_square in chess_util.get_diagonals(queen):
            if board.piece_type_at(diagonal_square) == chess.BISHOP and board.color_at(diagonal_square) != color:
                num_pieces_in_between = 0
                for in_between_square in chess.SquareSet.between(queen, diagonal_square):
                    if board.piece_at(in_between_square):
                        num_pieces_in_between += 1
                if num_pieces_in_between == 1:
                    value -= QUEEN_ALIGNED_PENALTY
        for file_or_rank_square in chess_util.get_file_and_rank_squares(queen):
            if board.piece_type_at(file_or_rank_square) == chess.ROOK and board.color_at(file_or_rank_square) != color:
                num_pieces_in_between = 0
                for in_between_square in chess.SquareSet.between(queen, file_or_rank_square):
                    if board.piece_at(in_between_square):
                        num_pieces_in_between += 1
                if num_pieces_in_between == 1:
                    value -= QUEEN_ALIGNED_PENALTY
    return value


# What makes a queen stronger or weaker
def get_queen_value(board, turn, free_to_take=None, free_to_trade=None, free_to_trade_value=0):
    evaluation = 0
    queens = board.pieces(chess.QUEEN, turn)
    for queen in queens:
        if queen == free_to_take:
            evaluation += PIECE_TYPES_TO_VALUES[chess.QUEEN] * \
                FREE_TO_TAKE_MODIFIER_PENALTY
        elif queen == free_to_trade:
            evaluation += FREE_TO_TRADE_MODIFIER * free_to_trade_value
        elif board.is_pinned(turn, queen) and board.piece_type_at(chess_util.get_pinner(board, queen)) in [chess.BISHOP, chess.ROOK]:
            pinner_piece_type = board.piece_type_at(
                chess_util.get_pinner(board, queen))
            evaluation += PIECE_TYPES_TO_VALUES[pinner_piece_type] * \
                FREE_TO_TRADE_MODIFIER
        else:
            evaluation += PIECE_TYPES_TO_VALUES[chess.QUEEN]
            if not board.is_pinned(turn, queen):
                evaluation += len(board.attacks(queen)) * QUEEN_ATTACK_VALUE
            evaluation += get_defended_bonus(board, queen)
    evaluation += get_queen_aligned_value(board, turn)
    return evaluation


def activate_king(board, color):
    max_distance_to_pawn = 7
    king = board.king(color)
    pawns = board.pieces(chess.PAWN, chess.WHITE).union(
        board.pieces(chess.PAWN, chess.BLACK))
    distance_to_pawn_bonus = get_eval(
        board, color, KING_DISTANCE_TO_PAWN_BONUS)
    value = 0
    for pawn in pawns:
        value += distance_to_pawn_bonus * \
            (max_distance_to_pawn - chess.square_distance(king, pawn))
    return value


def infiltrate_king(board, color):
    king = board.king(color)
    return chess_util.get_adjusted_rank(king, color)


# open and half open files towards the king put the king at risk
def get_open_file_to_king_penalty(board, color):
    penalty = 0
    if chess_util.get_num_major_pieces(board, not color) > 1 and not board.has_castling_rights(color):
        king = board.king(color)
        if chess_util.is_open_file(board, king):
            penalty += OPEN_FILE_TO_KING_PENALTY
        if chess_util.is_half_open_file(board, king):
            penalty += HALF_OPEN_FILE_TO_KING_PENALTY
        for adjacent_file in chess_util.get_adjacent_files(king):
            adjacent_square = chess.square(adjacent_file, 0)
            if chess_util.is_open_file(board, adjacent_square):
                penalty += OPEN_ADJACENT_FILE_TO_KING_PENALTY
            if chess_util.is_half_open_file(board, adjacent_square):
                penalty += HALF_OPEN_ADJACENT_FILE_TO_KING_PENALTY
    return penalty


def get_king_value(board, color, free_to_take=None, free_to_trade=None, free_to_trade_value=0):
    king = board.king(color)
    evaluation = 0
    # Todo: Testing this out
    if is_endgame(board, color):
        evaluation += infiltrate_king(board, color)
    else:
        evaluation += get_king_safety(board, color)
        #print("king safety =", get_king_safety(board, color))
    evaluation += activate_king(board, color)
    #print("activate king =", activate_king(board, color))
    evaluation += get_piece_on_bishop_color_penalty(board, king)
    evaluation += get_open_file_to_king_penalty(board, color)
    #print("piece on bishop color penalty =", get_piece_on_bishop_color_penalty(board, king))
    return evaluation


# How safe is color's king?
def get_king_safety(board, color):
    evaluation = 0
    # percentage of adjacent squares that are attacked
    percentage_attacked_adjacent = get_percent_attacked_adjacent(board, color)
    attacking_adjacent_value = -percentage_attacked_adjacent * \
        get_eval(board, color, ATTACKING_ADJACENT_EVAL)
    evaluation += attacking_adjacent_value
    #print("attacking adjacent =", attacking_adjacent_value)
    evaluation += get_king_square_safety(board, color)
    #print("king square safety =", get_king_square_safety(board, color))
    evaluation += get_pawn_wall_value(board, color)
    #print("pawn wall =", get_pawn_wall_value(board, color))
    return evaluation


# Favor putting the king on a square closer to the corner
def get_king_square_safety(board, color):
    king_square = board.king(color)
    if color == chess.WHITE:
        return get_eval(board, color, SQUARES_TO_WHITE_KING_SAFETY.get(king_square, 0))
    return get_eval(board, color, SQUARES_TO_BLACK_KING_SAFETY.get(king_square, 0))


def get_pawn_wall_value(board, color):
    king_square = board.king(color)
    # white checks pawns on rank + 1; black checks pawn on rank - 1
    color_rank_modifier = 1 if color else -1
    # square in front of king
    square_in_front = chess_util.add_rank(king_square, color_rank_modifier)

    close_wall_squares = [square_in_front, chess_util.add_file(
        square_in_front, -1), chess_util.add_file(square_in_front, 1)]
    close_wall_squares = list(filter(None, close_wall_squares))
    total_value = 0
    for square in close_wall_squares:
        if board.piece_type_at(square) == chess.PAWN:
            total_value += get_eval(board, color, CLOSE_PAWN_WALL_EVAL)

    far_wall_squares = [chess_util.add_rank(
        square, color_rank_modifier) for square in close_wall_squares]
    far_wall_squares = list(filter(None, far_wall_squares))
    for square in far_wall_squares:
        if board.piece_type_at(square) == chess.PAWN:
            total_value += get_eval(board, color, FAR_PAWN_WALL_EVAL)

    return total_value


# Delete: Too performance costly?
# How many moves will check color's king
def get_num_checks(board, color):
    undo_move = False
    if board.turn == color:
        if board.is_check():
            return 1
        board.push(chess.Move.null())
        undo_move = True
    num_checks = 0
    for move in board.legal_moves:
        if board.gives_check(move):
            num_checks += 1
    if undo_move:
        board.pop()
    return num_checks


# returns the percentage of squares adjacent to color's king that are attacked by not color
def get_percent_attacked_adjacent(board, color):
    adjacent_squares = chess_util.get_adjacent_squares(board.king(color))
    num_attacked_squares = sum(
        1 for adjacent_square in adjacent_squares if board.is_attacked_by(not color, adjacent_square))
    return 1.0 * num_attacked_squares / len(adjacent_squares)


def get_castling_eval(board, turn):
    if board.has_castling_rights(turn):
        return CAN_CASTLE_EVAL
    if has_castled(board, turn):
        return HAS_CASTLED_EVAL
    return 0


def has_castled(board, turn):
    print("Move stack =", board.move_stack)
    print("last move =", board.peek())
    starting_move_number = 0 if turn else 1
    print("num moves =", len(board.move_stack))
    for i in range(starting_move_number, len(board.move_stack), 2):
        print(i)
        move = board.move_stack[i]
        if board.is_castling(move):
            return True
    return False


# Is the opponent in check, and you are winning material
# Todo: Is this needed or is extend better here?
# Todo: Delete?
def get_check_to_win_material_tactic_value(board, piece):
    color = board.color_at(piece)
    if board.is_check() and color == board.turn:
        if chess_util.are_more_attackers_than_defenders(board, piece):
            return PIECE_TYPES_TO_VALUES[board.piece_type_at(piece)] * FREE_TO_TAKE_MODIFIER_PENALTY
        return chess_util.get_trade_value(board, piece) * FREE_TO_TRADE_MODIFIER
    return 0


# Pieces get a bonus for being defended
def get_defended_bonus(board, piece):
    color = board.color_at(piece)
    defenders = [defender for defender in board.attackers(
        color, piece) if not board.is_pinned(color, defender)]
    if len(defenders) >= 2:
        return DOUBLE_DEFENDED_BONUS
    elif len(defenders) == 1 and board.piece_type_at(defenders[0]) == chess.PAWN:
        return PAWN_DEFENDING_BONUS
    elif len(defenders) == 1:
        return DEFENDED_EVAL
    return 0


def get_evaluation_for_both_sides(get_evaluation, board, turn, *args):
    # print(get_evaluation.__name__)
    evaluation = get_evaluation(board, turn, *args) - \
        get_evaluation(board, not turn, *args)
    # print(evaluation)
    return evaluation


def extend_search(board, turn, check_tactics, extend):
    maximizing = board.turn == turn
    min_or_max = max if maximizing else min
    evaluation = float('-inf') if maximizing else float('inf')
    for move in board.legal_moves:
        # print()
        #print("move =", move.uci())
        board.push(move)
        evaluation = min_or_max(evaluation, evaluate_position(
            board, turn, check_tactics, extend))
        board.pop()
    return evaluation


# Search checks in the position
def extend_checks(board, turn, check_tactics, extend):
    maximizing = board.turn == turn
    min_or_max = max if maximizing else min
    # evaluation should be initialized to evaluation for current position
    evaluation = evaluate_position(board, turn, check_tactics, extend=False)
    for move in board.legal_moves:
        if board.gives_check(move):
            board.push(move)
            # if checks are bad, ignore them; if checks are good, update evaluation
            evaluation = min_or_max(evaluation, evaluate_position(
                board, turn, check_tactics, extend))
            board.pop()
    return evaluation


# Todo: Is this used?
def get_equal_or_greater_trade_moves(board: chess.Board) -> List[chess.Move]:
    moves = []
    for move in board.legal_moves:
        if board.is_en_passant(move):
            moves += move
        elif board.is_capture(move):
            if PIECE_TYPES_TO_ROUGH_VALUES[board.piece_type_at(move.from_square())] <= \
                    PIECE_TYPES_TO_ROUGH_VALUES[board.piece_type_at(move.to_square())]:
                moves += move
    return moves


# Todo: Finish implementing
# Extend fair trades, taking free pieces, good trades
def extend_trades(board: chess.Board, turn: chess.Color) -> int:
    for move in get_equal_or_greater_trade_moves(board):
        pass


# Check to see if player is getting mated
def search_getting_mated(board, turn, num_checks_left=2, num_checks_made=0):
    if board.is_checkmate():
        if board.turn == turn:
            return MIN_EVAL + num_checks_made
        else:
            return MAX_EVAL - num_checks_made
    if num_checks_left == 0:
        return 0
    # Search all possible moves when in check
    if board.is_check():
        evaluation = None
        for move in board.legal_moves:
            board.push(move)
            search_evaluation = search_getting_mated(
                board, turn, num_checks_left, num_checks_made)
            board.pop()
            # At least one line does not lead to forced mate
            if search_evaluation == 0:
                return search_evaluation
            if evaluation is None:
                evaluation = search_evaluation
            # A check was intercepted with another check leading to forced mate
            elif evaluation != search_evaluation:
                return 0
        return evaluation
    else:
        # Search checks
        for move in board.legal_moves:
            evaluation = 0
            board.push(move)
            if board.is_check():
                evaluation = search_getting_mated(
                    board, turn, num_checks_left-1, num_checks_made+1)
            board.pop()
            if evaluation != 0:
                return evaluation
    return 0


# Returns centipawn (pawn worth 100 points) evaluation
# A positive number is good for turn while negative is bad
# If quiet search is being used then check_tactics will not be needed since the search will continue until tactics are removed from the position
# extend can be used to extend the search one level deeper in potential tactical positions
def evaluate_position(board, turn, check_tactics=True, extend=True):
    if board.is_checkmate():
        if board.turn == turn:
            return MIN_EVAL
        else:
            return MAX_EVAL
    # Is can_claim_threefold_repetition() affecting performance?
    if chess_util.is_draw(board):
        return DRAW_EVAL
    if extend:
        forced_mate_evaluation = search_getting_mated(board, turn)
        if forced_mate_evaluation != 0:
            return forced_mate_evaluation
        if board.is_check():
            return extend_search(board, turn, check_tactics, extend=False)
        else:
            return extend_checks(board, turn, check_tactics, extend)
    if endgame.is_endgame(board):
        return endgame.evaluate_position(board, turn)

    free_to_take = chess_util.get_most_valuable_free_to_take(board)
    free_to_trade, free_to_trade_value = chess_util.get_most_valuable_free_to_trade(
        board)
    if free_to_take is not None and free_to_trade is not None:
        free_to_take_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(
            free_to_take)]
        free_to_trade_value_won = PIECE_TYPES_TO_VALUES[board.piece_type_at(
            free_to_trade)] - free_to_trade_value
        # More value in taking free_to_take
        if free_to_take_value > free_to_trade_value_won:
            free_to_trade, free_to_trade_value = None, 0
        # More value in taking free_to_trade
        else:
            free_to_take = None

    evaluation = 0
    evaluation += get_evaluation_for_both_sides(
        get_pawn_value, board, turn, free_to_take)
    evaluation += get_evaluation_for_both_sides(
        get_knight_value, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    evaluation += get_evaluation_for_both_sides(
        get_bishop_value, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    evaluation += get_evaluation_for_both_sides(
        get_rook_value, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    evaluation += get_evaluation_for_both_sides(
        get_queen_value, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    evaluation += get_evaluation_for_both_sides(
        get_king_value, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    evaluation += get_evaluation_for_both_sides(
        attacking_stronger_pieces, board, turn, free_to_take, free_to_trade, free_to_trade_value)
    # print(board)
    #print("evaluation = ", evaluation)
    if board.can_claim_draw():
        if turn == board.turn:
            # turn can decide to go for the draw or not
            evaluation = max(evaluation, DRAW_EVAL)
        else:
            # Not turn will decide to go for a draw if evaluation is good for turn
            evaluation = min(evaluation, DRAW_EVAL)
    # Avoid repetions if you are in a better position; favor repetions if you are in a worse position
    if board.is_repetition(count=2):
        evaluation /= 2
    return evaluation


def get_victim_value(board, move):
    if not board.is_capture(move):
        return 0
    if board.is_en_passant(move):
        return PIECE_TYPES_TO_VALUES[chess.PAWN]
    return PIECE_TYPES_TO_VALUES[board.piece_type_at(move.to_square)]


# Gets simpler evaluation based on old evaluation
def evaluate_position_after_capture(board, turn, old_evaluation):
    if board.is_checkmate():
        if board.turn == turn:
            return MIN_EVAL
        else:
            return MAX_EVAL

    if chess_util.is_draw(board):
        return DRAW_EVAL

    if not board.move_stack or not old_evaluation:
        return evaluate_position(board, turn)

    move = board.pop()
    victim_value = get_victim_value(board, move)
    board.push(move)
    return -old_evaluation - victim_value
