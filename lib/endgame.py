import chess
import chess_util

# Todo: How to win queen vs rook, queen vs knight, queen vs bishop, etc.

WINNING_EVAL = 500_000
WINNING_PAWN_EVAL = 400_000
DRAW_EVAL = 0

PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900}
NON_PAWN_PIECE_TYPES = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
PIECE_TYPES = [chess.PAWN] + NON_PAWN_PIECE_TYPES

EDGE_EVAL = 5
CLOSE_EVAL = 1


# returns between 0 and 3
def get_distance_from_center(rank_or_file):
	return rank_or_file - 4 if rank_or_file > 3 else 3 - rank_or_file	

# push weak king to corner
# square values to value the edge higher
def push_to_corner(square):
	rank = chess.square_rank(square)
	rank_distance_from_center = get_distance_from_center(rank)
	file = chess.square_file(square)
	file_distance_from_center = get_distance_from_center(file)
	return (rank_distance_from_center**2 + file_distance_from_center**2) * EDGE_EVAL

# Returns 
def push_close(square1, square2):
	distance = chess.square_distance(square1, square2)
	return -distance * CLOSE_EVAL

def push_close_non_pawns(board, square):
	close_total = 0
	color = not board.color_at(square)
	for piece_type in NON_PAWN_PIECE_TYPES + [chess.KING]:
		pieces = board.pieces(piece_type, color)
		for piece in pieces:
			close_total += push_close(piece, square)
	return close_total

# Returns (color has rook or queen, color has any pieces besides king)
def has_pieces(board, color):
	rook_or_queen_piece_types = [chess.ROOK, chess.QUEEN]
	other_piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP]
	has_rook_or_queen = False
	has_pieces = False
	for piece_type in rook_or_queen_piece_types:
		for piece in board.pieces(piece_type, color):
			if not chess_util.is_free_to_take_this_turn(board, piece):
				has_rook_or_queen = True
				has_pieces = True
				break
	for piece_type in other_piece_types:
		if board.pieces(piece_type, color):
			has_pieces = True
			break
	return (has_rook_or_queen, has_pieces)

# Returns True if color has pawns
def has_pawns(board, color):
	if board.pieces(chess.PAWN, color):
		return True
	return False

def get_strong_color(board):
	_, white_has_pieces = has_pieces(board, chess.WHITE)
	return chess.WHITE if white_has_pieces else chess.BLACK

# Returns the number of moves required to promote the pawn assuming there are no pieces in the way
def get_num_moves_to_promote(pawn, color):
	promoting_rank = 7
	adjusted_rank = chess_util.get_adjusted_rank(pawn, color)
	max_moves_to_promote = 5
	return min(max_moves_to_promote, promoting_rank - adjusted_rank)

# Returns the square a pawn would promote on
def get_promotion_square(pawn, color):
	file = chess.square_file(pawn)
	if color: # white pawn
		rank = 7
		return chess.square(file, rank)
	# black pawn
	rank = 0
	return chess.square(file, rank)

def is_pawn_outside_of_square(board, pawn):
	pawn_color = board.color_at(pawn)
	chasing_king = board.king(not pawn_color)
	num_moves_to_promote = get_num_moves_to_promote(pawn, pawn_color)
	promotion_square = get_promotion_square(pawn, pawn_color)
	num_king_moves = chess.square_distance(chasing_king, promotion_square)
	if (board.turn == pawn_color and num_moves_to_promote < num_king_moves) or \
		(board.turn != pawn_color and num_moves_to_promote < num_king_moves - 1):
		return True
	return False

# Returns the square containing the pawn the opponent's king cannot reach before promoting; None otherwise
def get_pawn_outside_of_square(board, pawn_color):
	for pawn in board.pieces(chess.PAWN, pawn_color):
		if is_pawn_outside_of_square(board, pawn):
			return pawn
	return None

def get_material_value(board, color):
	material_value = 0
	for piece_type in PIECE_TYPES:
		pieces = board.pieces(piece_type, color)
		for piece in pieces:
			if not chess_util.is_free_to_take_this_turn(board, piece):
				material_value += PIECE_TYPES_TO_VALUES[piece_type]
	return material_value

# Is the outcome of the endgame known
def is_endgame(board):
	white_has_rook_or_queen, white_has_pieces = has_pieces(board, chess.WHITE)
	black_has_rook_or_queen, black_has_pieces = has_pieces(board, chess.BLACK)
	return (white_has_rook_or_queen and not black_has_pieces) or (black_has_rook_or_queen and not white_has_pieces) or \
		(has_pawns(board, chess.WHITE) and not black_has_pieces and get_pawn_outside_of_square(board, chess.WHITE)) or \
		(has_pawns(board, chess.BLACK) and not white_has_pieces and get_pawn_outside_of_square(board, chess.BLACK))

# A positive number is good for turn while negative is bad
# Prerequisite: is_endgame should be True
def evaluate_position(board, turn):
	strong_color = get_strong_color(board)
	modifier = 1 if turn == strong_color else -1
	strong_king = board.king(strong_color)
	weak_king = board.king(not strong_color)
	has_rook_or_queen, _ = has_pieces(board, strong_color)
	evaluation = 0
	if has_rook_or_queen:
		evaluation = WINNING_EVAL
		#print("push_to_corner =", push_to_corner(weak_king))
		#print("push_close =", push_close(weak_king, strong_king))
		evaluation += push_to_corner(weak_king)
		# Todo: Should this be in?
		#evaluation += push_close(weak_king, strong_king)
		evaluation += push_close_non_pawns(board, weak_king)
		evaluation += get_material_value(board, strong_color)
	else:
		promoting_pawn = get_pawn_outside_of_square(board, strong_color)
		if promoting_pawn:
			evaluation = WINNING_PAWN_EVAL
			evaluation += push_close(promoting_pawn, get_promotion_square(promoting_pawn, strong_color))
		else:
			evaluation = DRAW_EVAL
	#print(board)
	#print("evaluation = ", evaluation)
	return modifier * evaluation
