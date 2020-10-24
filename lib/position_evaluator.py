import chess
from collections import defaultdict

MAX_EVAL = 1_000_000
MIN_EVAL = -MAX_EVAL
DRAW_EVAL = 0

# General
ATTACK_VALUE = 3
FREE_TO_TAKE_MODIFIER = .9
FREE_TO_TAKE_NOT_TURN_MODIFIER = .1
DEFENDED_EVAL = 10

# Pawn
PAWN_IN_CENTER_EVAL = 30
# Bonus for pawn being closer to the center
CENTRAL_PAWN_EVAL = 3
RANK_PAWN_EVAL = 2
ISOLATED_PAWN_EVAL = 30
PASSED_PAWN_EVAL = 30

# Knight
KNIGHT_RANK_EVAL = [0, 5, 10, 15, 30, 50, 40, 20]
KNIGHT_IN_CENTER_EVAL = 40
KNIGHT_IN_SECOND_RING_EVAL = 30

# Rook
CONNECTED_ROOKS_EVAL = 30

# King
POTENTIAL_CHECK_EVAL = 5
ATTACKING_ADJACENT_EVAL = 100

PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 320, chess.ROOK: 500, chess.QUEEN: 900}
PIECE_TYPES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
ALL_PIECE_TYPES = PIECE_TYPES + [chess.KING]

CENTER = [chess.D4, chess.D5, chess.E4, chess.E5]
SECOND_RING = [chess.C3, chess.C4, chess.C5, chess.C6, chess.D3, chess.D6, chess.E3, chess.E6, chess.F3, chess.F4, chess.F5, chess.F6]
RIM = [chess.A1, chess.A2, chess.A3, chess.A4, chess.A5, chess.A6, chess.A7, chess.A8, chess.B1, chess.B8] #need to finish

# Are there any pieces free to take for color
def count_free_to_take(board, turn, color):
	evaluation = 0
	modifier = FREE_TO_TAKE_MODIFIER if turn == color else FREE_TO_TAKE_NOT_TURN_MODIFIER
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, not color)
		for piece in pieces:
			# attacked by color and not defended by not color
			if board.is_attacked_by(color, piece) and not board.is_attacked_by(not color, piece):
				evaluation += PIECE_TYPES_TO_VALUES[piece_type] * modifier
	return evaluation

# Are you attacking a defended piece with something of lesser value (i.e. threatening a trade in your favor)
def attacking_stronger_pieces(board, color):
	evaluation = 0
	modifier = FREE_TO_TAKE_MODIFIER if board.turn == color else FREE_TO_TAKE_NOT_TURN_MODIFIER
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, not color)
		for piece in pieces:
			# attacked by color and defended by not color
			if board.is_attacked_by(color, piece) and board.is_attacked_by(not color, piece):
				attackers = board.attackers(color, piece)
				# difference between attacking piece value and attacked piece value
				max_difference = 0
				for attacker in attackers:
					if board.piece_type_at(attacker) != chess.KING:
						attacker_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(attacker)]
						piece_value = PIECE_TYPES_TO_VALUES[piece_type]
						if attacker_value < piece_value:
							max_difference = max(max_difference, piece_value - attacker_value)
				evaluation += max_difference * modifier
	return evaluation

# e.g. White has queen, rook, two bishops, and three pawns
def get_total_piece_value(board, turn):
	evaluation = 0
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, turn)
		evaluation += len(pieces) * PIECE_TYPES_TO_VALUES[piece_type]
	return evaluation
	
def get_num_isolated_pawns(pawns):
	num_isolated_pawns = 0
	pawn_files = list(map(chess.square_file, pawns))
	for pawn_file in pawn_files:
		if pawn_file - 1 not in pawn_files and pawn_file + 1 not in pawn_files:
			num_isolated_pawns += 1
	return num_isolated_pawns

def get_num_passed_pawns(board, turn):
	num_passed_pawns = 0
	own_pawns = board.pieces(chess.PAWN, turn)
	enemy_pawns = board.pieces(chess.PAWN, not turn)
	enemy_pawn_files = list(map(chess.square_file, enemy_pawns))
	enemy_pawn_files_to_pawns = defaultdict(list) # dictionary with default values of empty list
	for enemy_pawn in enemy_pawns:
		enemy_pawn_files_to_pawns[chess.square_file(enemy_pawn)].append(enemy_pawn)
	for own_pawn in own_pawns:
		own_pawn_file = chess.square_file(own_pawn)
		if own_pawn_file - 1 not in enemy_pawn_files and own_pawn_file not in enemy_pawn_files and own_pawn_file + 1 not in enemy_pawn_files:
			num_passed_pawns += 1
		else:
			own_pawn_rank = chess.square_rank(own_pawn)
			is_passed = True
			for enemy_pawn in (enemy_pawn_files_to_pawns[own_pawn_file - 1] + enemy_pawn_files_to_pawns[own_pawn_file] + enemy_pawn_files_to_pawns[own_pawn_file + 1]):
				if turn: # White
					if chess.square_rank(enemy_pawn) > own_pawn_rank:
						is_passed = False
						break
				else: # Black
					if chess.square_rank(enemy_pawn) < own_pawn_rank:
						is_passed = False
						break
			if is_passed:
				num_passed_pawns += 1
	return num_passed_pawns	

# Pawns closer to the center files are worth more
def get_center_pawn_eval(pawns):
	evaluation = 0
	file_to_center_val = {0:0, 1:1, 2:2, 3:3, 4:3, 5:2, 6:1, 7:0}
	for pawn in pawns:
		evaluation += file_to_center_val[chess.square_file(pawn)] * CENTRAL_PAWN_EVAL
	return evaluation

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

# What makes a pawn stronger or weaker
def get_pawn_value(board, turn):
	evaluation = 0
	pawns = board.pieces(chess.PAWN, turn)
	for pawn in pawns:
		if pawn in CENTER:
			evaluation += PAWN_IN_CENTER_EVAL
	evaluation -= get_num_isolated_pawns(pawns) * ISOLATED_PAWN_EVAL
	evaluation += get_num_passed_pawns(board, turn) * PASSED_PAWN_EVAL
	evaluation += get_center_pawn_eval(pawns)
	evaluation += get_rank_pawn_eval(pawns, turn)
	return evaluation

def get_knight_rank_eval(knights, turn):
	evaluation = 0
	for knight in knights:
		# ranges from 0 to 7
		rank_val = chess.square_rank(knight)
		max_rank_val = 7
		if (turn == chess.BLACK):
			rank_val = max_rank_val - rank_val
		evaluation += KNIGHT_RANK_EVAL[rank_val]
	return evaluation

# What makes a knight stronger or weaker
def get_knight_value(board, turn):
	evaluation = 0
	knights = board.pieces(chess.KNIGHT, turn)
	for knight in knights:
		evaluation += len(board.attacks(knight)) * ATTACK_VALUE
	evaluation += get_knight_rank_eval(knights, turn)
	return evaluation

# What makes a bishop stronger or weaker
def get_bishop_value(board, turn):
	evaluation = 0
	pieces = board.pieces(chess.BISHOP, turn)
	for bishop in pieces:
		evaluation += len(board.attacks(bishop)) * ATTACK_VALUE
	return evaluation

def get_connected_rooks_value(board, rooks):
	evaluation = 0
	rooks = list(rooks)
	if len(rooks) == 2 and rooks[0] in board.attacks(rooks[1]):
		evaluation += CONNECTED_ROOKS_EVAL
	return evaluation	

# What makes a rook stronger or weaker
def get_rook_value(board, turn):
	evaluation = 0
	rooks = board.pieces(chess.ROOK, turn)
	for rook in rooks:
		evaluation += len(board.attacks(rook)) * ATTACK_VALUE
	evaluation += get_connected_rooks_value(board, rooks)
	return evaluation

# What makes a queen stronger or weaker
def get_queen_value(board, turn):
	evaluation = 0
	queens = board.pieces(chess.QUEEN, turn)
	for queen in queens:
		evaluation += len(board.attacks(queen)) * ATTACK_VALUE
	return evaluation

# How safe is color's king?
def get_king_safety(board, color):
	num_checks = get_num_checks(board, color)
	# percentage of adjacent squares that are attacked
	percentage_attacked_adjacent = get_percent_attacked_adjacent(board, color)
	return -num_checks * POTENTIAL_CHECK_EVAL - percentage_attacked_adjacent * ATTACKING_ADJACENT_EVAL

# How many moves will check color's king
def get_num_checks(board, color):
	undo_move = False
	if board.turn == color:
		if board.is_check():
			return 1
		board.push(chess.Move.null())
		undo_move = True
	num_checks = 0;
	for move in board.legal_moves:
		# in later version of python-chess
		# if board.gives_check(move):
		board.push(move)
		if board.is_check():
			num_checks += 1
		board.pop()
	if undo_move:
		board.pop()
	return num_checks

def get_adjacent_squares(square):
	return {x for x in chess.SQUARES if chess.square_distance(x, square) == 1}

# returns the percentage of squares adjacent to color's king that are attacked by not color
def get_percent_attacked_adjacent(board, color):
	adjacent_squares = get_adjacent_squares(board.king(color))
	num_attacked_squares = sum(1 for adjacent_square in adjacent_squares if board.is_attacked_by(not color, adjacent_square))
	return 1.0 * num_attacked_squares / len(adjacent_squares)

# Pinned pieces are weaker
def check_for_pins(board, turn):
	evaluation = 0
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, turn)
		for piece in pieces:
			if board.is_pinned(turn, piece):
				evaluation -= PIECE_TYPES_TO_VALUES[piece_type] / 2
	return evaluation

def get_defended_value(board, turn):
	evaluation = 0
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, turn)
		for piece in pieces:
			if board.is_attacked_by(turn, piece):
				evaluation += DEFENDED_EVAL
	return evaluation


def evaluate_position(board, turn):
	if board.is_checkmate():
		if board.turn == turn:
			return MIN_EVAL
		else:
			return MAX_EVAL
	# Is can_claim_draw() affecting performance?
	if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
		return DRAW_EVAL
	evaluation = 0
	evaluation += get_total_piece_value(board, turn) - get_total_piece_value(board, not turn)
	evaluation += get_pawn_value(board, turn) - get_pawn_value(board, not turn)
	evaluation += get_knight_value(board, turn) - get_knight_value(board, not turn)
	evaluation += get_bishop_value(board, turn) - get_bishop_value(board, not turn)
	evaluation += get_rook_value(board, turn) - get_rook_value(board, not turn)
	evaluation += get_queen_value(board, turn) - get_queen_value(board, not turn)
	evaluation += get_king_safety(board, turn) - get_king_safety(board, not turn)
	evaluation += check_for_pins(board, turn) - check_for_pins(board, not turn)
	evaluation += get_defended_value(board, turn) - get_defended_value(board, not turn)
	# board.turn = who's turn is it currently in the minimax evaluation
	# turn = the turn of the player whose best move we are trying to find
	evaluation += count_free_to_take(board, board.turn, turn) - count_free_to_take(board, board.turn, not turn)
	evaluation += attacking_stronger_pieces(board, turn) - attacking_stronger_pieces(board, not turn)
	#print(board)
	#print("evaluation = ", evaluation)
	return evaluation

