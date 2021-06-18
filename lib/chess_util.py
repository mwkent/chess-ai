# Handles chess related utility functions
import chess

#Todo: Fix free to take - For instance pawn defended by pawn can't be taken by queen and rook
# Also pieces can defend/attack through opponent's pieces

MAX_RANK = 7
MAX_FILE = 7

MOST_VALUABLE_TO_LEAST_PIECE_TYPES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
MINOR_PIECES = [chess.KNIGHT, chess.BISHOP]
MAJOR_PIECES = [chess.ROOK, chess.QUEEN]
PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 10_000}

# Returns True if the piece is on a light square
# piece must be a Square
def is_piece_on_light_square(piece):
	return on_light_squares(chess.SquareSet.from_square(piece))

# Returns True if the piece is on a dark square
# piece must be a Square
def is_piece_on_dark_square(piece):
	return on_dark_squares(chess.SquareSet.from_square(piece))

# Returns True if one of the pieces is on a light square
# pieces must be a SquareSet
def on_light_squares(pieces):
	return int(pieces) & chess.BB_LIGHT_SQUARES

# Returns True if one of the pieces is on a dark square
# pieces must be a SquareSet
def on_dark_squares(pieces):
	return int(pieces) & chess.BB_DARK_SQUARES

# Returns SquareSet containing all squares on the diagonals associated with the square
def get_diagonals(square):
	file = chess.square_file(square)
	rank = chess.square_rank(square)
	diagonal_squares = chess.SquareSet()
	for file_mod in [-1, 1]:
		for rank_mod in [-1, 1]:
			diagonal_file = file + file_mod
			diagonal_rank = rank + rank_mod
			if diagonal_file >= chess.square_file(chess.A1) and diagonal_file <= chess.square_file(chess.H8) \
			and diagonal_rank >= chess.square_rank(chess.A1) and diagonal_rank <= chess.square_rank(chess.H8):
				diagonal_squares = diagonal_squares.union(chess.SquareSet.ray(square, chess.square(diagonal_file, diagonal_rank)))
	return diagonal_squares

# Returns a list of the files adjacent to square
# e.g. 0 is the A file, 7 is the H file
def get_adjacent_files(square):
	file = chess.square_file(square)
	adjacent_files = [file-1, file+1]
	return [adjacent_file for adjacent_file in adjacent_files if adjacent_file >= 0 and adjacent_file <= MAX_FILE]

# Returns SquareSet containing all squares on the same file associated with the square
def get_file_squares(square):
	same_file_square = add_rank(square, 1)
	if not same_file_square:
		same_file_square = add_rank(square, -1)
	return chess.SquareSet.ray(square, same_file_square)

# Returns SquareSet containing all squares on the same rank and file associated with the square
def get_file_and_rank_squares(square):
	file = chess.square_file(square)
	rank = chess.square_rank(square)
	result_squares = chess.SquareSet()
	for mod in [-1, 1]:
		result_file = file + mod
		if result_file >= chess.square_file(chess.A1) and result_file <= chess.square_file(chess.H8):
			result_squares = result_squares.union(chess.SquareSet.ray(square, chess.square(result_file, rank)))
		result_rank = rank + mod
		if result_rank >= chess.square_file(chess.A1) and result_rank <= chess.square_file(chess.H8):
			result_squares = result_squares.union(chess.SquareSet.ray(square, chess.square(file, result_rank)))
	return result_squares

# Checks if the file containing square has one pawn on it
def is_half_open_file(board, square):
	file_squares = get_file_squares(square)
	pawn_count = 0
	for file_square in file_squares:
		if board.piece_type_at(file_square) == chess.PAWN:
			pawn_count += 1
	return pawn_count == 1

# Checks if the file containing square has no pawns on it
def is_open_file(board, square):
	file_squares = get_file_squares(square)
	for file_square in file_squares:
		if board.piece_type_at(file_square) == chess.PAWN:
			return False
	return True

# Returns the square + num_ranks or None if square is not in the board
# e.g., A1 + 1 = A2, A8 + 1 = None
def add_rank(square, num_ranks):
	if square is not None:
		result = square + num_ranks * 8
		if result >= chess.A1 and result <= chess.H8:
			return result
	return None

# Returns the square + num_files or None if square is not in the board
# e.g., A1 + 1 = B1, H1 + 1 = None
def add_file(square, num_files):
	if square is not None:
		result = square + num_files
		rank = chess.square_rank(square)
		if chess.square_rank(result) == rank:
			return result
	return None

def add_rank_and_file(square, num_ranks, num_files):
	return add_file(add_rank(square, num_ranks), num_files)

# Returns squares 1 king distance away from square
def get_adjacent_squares(square):
	return {x for x in chess.SQUARES if chess.square_distance(x, square) == 1}

# Returns 0 to 7 for the rank where the values are flipped if color is black
def get_adjusted_rank(square, color):
	return chess.square_rank(square) if color else MAX_RANK - chess.square_rank(square)

# How many minor pieces (e.g. bishops and knights) does color have?
def get_num_minor_pieces(board, color):
	return len(board.pieces(chess.BISHOP, color)) + len(board.pieces(chess.KNIGHT, color))

# How many major pieces (e.g. rooks and queens) does color have?
def get_num_major_pieces(board, color):
	return len(board.pieces(chess.ROOK, color)) + len(board.pieces(chess.QUEEN, color))

# Does color have any minor or major pieces?
def has_minor_or_major_pieces(board, color):
	return any(board.pieces(piece_type, color) for piece_type in MINOR_PIECES + MAJOR_PIECES)

# Does color have knights and no bishops, rooks, or queens?
def has_only_knight_minor_or_major_pieces(board, color):
	return board.pieces(chess.KNIGHT, color) and not any(board.pieces(piece_type, color) for piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN])

# Returns the piece in pieces with the least value
# King is considered the highest valued piece, then queen, etc.
def get_min_valued_piece(board, pieces):
	min_value_piece = None
	for piece in pieces:
		piece_type = board.piece_type_at(piece)
		if min_value_piece == None or board.piece_type_at(min_value_piece) == chess.KING or \
			(piece_type != chess.KING and PIECE_TYPES_TO_VALUES[piece_type] < PIECE_TYPES_TO_VALUES[board.piece_type_at(min_value_piece)]):
			min_value_piece = piece
	return min_value_piece

def get_forward_knight_moves(board, knight):
	knight_color = board.color_at(knight)
	knight_adjusted_rank = get_adjusted_rank(knight, knight_color)
	return [knight_move for knight_move in board.attacks(knight) if get_adjusted_rank(knight_move, knight_color) > knight_adjusted_rank]

# Checks if a bishop is pinned to the king on a file or rank
def is_bishop_pinned(board, bishop, color):
	if board.is_pinned(color, bishop):
		squares = list(board.pin(color, bishop))
		# Pin is on a file or rank
		if chess.square_file(squares[0]) == chess.square_file(squares[1]) or \
			chess.square_rank(squares[0]) == chess.square_rank(squares[1]):
			return True
	return False

# Checks if a rook is pinned to the king on a diagonal
def is_rook_pinned(board, rook, color):
	if board.is_pinned(color, rook):
		squares = list(board.pin(color, rook))
		# Pin is on a diagonal
		if chess.square_file(squares[0]) != chess.square_file(squares[1]) and \
			chess.square_rank(squares[0]) != chess.square_rank(squares[1]):
			return True
	return False

# Can the piece be taken by an enemy piece
def can_piece_be_captured(board, piece):
	color = not board.color_at(piece)
	return any(attacker for attacker in board.attackers(color, piece) if can_piece_capture(board, attacker, piece))

# Can attacking piece take attacked piece
# Assumes that attacking_piece is actually attacking attacked_piece
def can_piece_capture(board, attacking_piece, attacked_piece):
	color = board.color_at(attacking_piece)
	if board.is_pinned(color, attacking_piece) and attacked_piece not in board.pin(color, attacking_piece):
		return False
	return True

# Gets attackers of square that are part of a battery of attackers (param)
def get_battery_attackers(board, square, color, attackers):
	battery_attackers = []
	for attacker in attackers:
		if board.piece_type_at(attacker) in [chess.PAWN, chess.BISHOP, chess.ROOK, chess.QUEEN]:
			# Pieces attacking the attacker; should not include existing attackers or attacked piece
			attacker_attackers = [attacker_attacker for attacker_attacker in board.attackers(color, attacker) \
				if attacker_attacker != square and attacker_attacker not in attackers]
			for attacker_attacker in attacker_attackers:
				# A battery is formed attacking the square
				if board.piece_type_at(attacker_attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN] \
					and not board.is_pinned(color, attacker_attacker) \
					and attacker_attacker in chess.SquareSet.ray(square, attacker):
					battery_attackers.append(attacker_attacker)
	return battery_attackers

# Get the pieces of color attacking square
# Currently considers only batteries of two pieces
# Todo: update to use get_battery_attackers function
def get_attackers(board, square, color):
	attackers = [attacker for attacker in board.attackers(color, square) if can_piece_capture(board, attacker, square)]
	# Check batteries
	for attacker in attackers:
		if board.piece_type_at(attacker) in [chess.PAWN, chess.BISHOP, chess.ROOK, chess.QUEEN]:
			# Pieces attacking the attacker; should not include existing attackers or attacked piece
			attacker_attackers = [attacker_attacker for attacker_attacker in board.attackers(color, attacker) \
				if attacker_attacker != square and attacker_attacker not in attackers]
			for attacker_attacker in attacker_attackers:
				# A battery is formed attacking the square
				if board.piece_type_at(attacker_attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN] \
					and not board.is_pinned(color, attacker_attacker) \
					and attacker_attacker in chess.SquareSet.ray(square, attacker):
					attackers.append(attacker_attacker)
	return attackers

# Get first attackers - the pieces of color that can move to square first
# Batteries not included, kings currently included
def get_first_attackers_and_defenders(board, square):
	defend_color = board.color_at(square)
	attackers = [attacker for attacker in board.attackers(not defend_color, square) if can_piece_capture(board, attacker, square)]
	defenders = [attacker for attacker in board.attackers(defend_color, square) if can_piece_capture(board, attacker, square)]
	return attackers, defenders

# Get second attackers and defenders - the attackers and defenders who can't move to square first
# i.e. pieces that may be in a battery or are pinned
# Technically, pinned pieces could be first attackers or defenders
def get_second_attackers_and_defenders(board, square, first_attackers, first_defenders):
	defend_color = board.color_at(square)
	second_attackers = get_battery_attackers(board, square, not defend_color, first_attackers)
	second_defenders = get_battery_attackers(board, square, defend_color, first_defenders)
	
	attackers = first_attackers + second_attackers
	defenders = first_defenders + second_defenders
	pinned_attackers, pinned_defenders = get_pinned_attackers_and_defenders(board, attackers, defenders, square)
	second_attackers += pinned_attackers
	second_defenders += pinned_defenders
	
	# Todo: Is there a better way to solve this?
	# Need to check if there are batteries being formed with pinned attackers and defenders as well
	second_attackers += get_battery_attackers(board, square, not defend_color, pinned_attackers)
	second_defenders += get_battery_attackers(board, square, defend_color, pinned_defenders)
	return second_attackers, second_defenders

# Get the number of pieces of color attacking square
# Currently considers only batteries of two pieces
def count_attackers(board, square, color):
	return len(get_attackers(board, square, color))

# Returns the piece that is pinning pinned_piece to the king
def get_pinner(board, pinned_piece):
	pinned_color = board.color_at(pinned_piece)
	if board.is_pinned(pinned_color, pinned_piece):
		pin_ray = board.pin(pinned_color, pinned_piece)
		for attacker in board.attackers(not pinned_color, pinned_piece):
			if attacker in pin_ray:
				return attacker
	return None

# Todo: Not considering battery attackers that are pinned?
def get_pinned_attackers_and_defenders(board, attackers, defenders, piece):
	defend_color = board.color_at(piece)
	pinned_attackers = []
	all_attackers = board.attackers(not defend_color, piece)
	all_defenders = board.attackers(defend_color, piece)
	for attacker in all_attackers:
		if (not can_piece_capture(board, attacker, piece)) and \
			get_pinner(board, attacker) in all_defenders:
			pinned_attackers.append(attacker)
	pinned_defenders = []
	for defender in all_defenders:
		if (not can_piece_capture(board, defender, piece)) and \
			get_pinner(board, defender) in all_attackers:
			pinned_defenders.append(defender)
	return pinned_attackers, pinned_defenders

# Are the pinner and pinned piece attacking the same squares
# pinned_side_attackers: the attackers of piece on the side of the pinned piece(s)
# pinner_side_attackers: the attackers of piece on the side of the pinner piece(s)
def get_num_pinner_and_pinned_piece_attacker_pairs(board, pinned_side_attackers, pinner_side_attackers, piece):
	num_pinner_and_pinned_piece_attacking_pairs = 0
	for pinned_side_attacker in pinned_side_attackers:
		if (board.is_pinned(board.color_at(pinned_side_attacker), pinned_side_attacker) and \
			get_pinner(board, pinned_side_attacker) in pinner_side_attackers):
			num_pinner_and_pinned_piece_attacking_pairs += 1
	return num_pinner_and_pinned_piece_attacking_pairs

def are_more_attackers_than_defenders(board, piece, attack_color=None):
	color = board.color_at(piece)
	if attack_color is not None:
		color = not attack_color
	defenders = get_attackers(board, piece, color)
	attackers = get_attackers(board, piece, not color)
	num_defenders = len(defenders)
	num_attackers = len(attackers)
	# Todo: Not considering batteries here
	all_defenders = board.attackers(color, piece)
	all_attackers = board.attackers(not color, piece)
	num_defenders += get_num_pinner_and_pinned_piece_attacker_pairs(board, all_defenders, attackers, piece)
	num_attackers += get_num_pinner_and_pinned_piece_attacker_pairs(board, all_attackers, defenders, piece)
	return num_attackers > num_defenders

def get_attackers_and_defenders(board, piece):
	color = board.color_at(piece)
	first_attackers, first_defenders = get_first_attackers_and_defenders(board, piece)
	second_attackers, second_defenders = get_second_attackers_and_defenders(board, piece, first_attackers, first_defenders)
	return first_attackers, second_attackers, first_defenders, second_defenders

# Can you take piece and win material
def is_free_to_take(board, piece):
	color = board.color_at(piece)
	# e.g. if it's white's turn, a white piece cannot be free to take
	if board.turn == color:
		return False
	first_attackers, second_attackers, first_defenders, second_defenders = get_attackers_and_defenders(board, piece)
	num_attackers = len(first_attackers) + len(second_attackers)
	num_defenders = len(first_defenders) + len(second_defenders)
	first_attackers.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[board.piece_type_at(piece)])
	first_defenders.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[board.piece_type_at(piece)])
	if len(first_attackers) >= 2:
		all_defenders = first_defenders + second_defenders
		lowest_two_attacker_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(first_attackers[0])] + \
			PIECE_TYPES_TO_VALUES[board.piece_type_at(first_attackers[1])]
		if all(PIECE_TYPES_TO_VALUES[board.piece_type_at(defender)] > lowest_two_attacker_value for defender in all_defenders):
			return True
	if num_attackers > num_defenders:
		if num_defenders == 0:
			return True
		if not first_attackers:
			return False
		if not first_defenders:
			return True
		min_value_attacker = first_attackers[0]
		min_value_defender = first_defenders[0]
		if num_defenders == 1 and board.piece_type_at(min_value_defender) == chess.KING:
			return True
		if PIECE_TYPES_TO_VALUES[board.piece_type_at(min_value_attacker)] < \
			PIECE_TYPES_TO_VALUES[board.piece_type_at(piece)] + PIECE_TYPES_TO_VALUES[board.piece_type_at(min_value_defender)]:
			return True
	return False

# Are there more attackers than defenders?
# Todo: Delete - does not consider value of piece being attacked and defender
def is_free_to_take3(board, piece):
	color = board.color_at(piece)
	# e.g. if it's white's turn, a white piece cannot be free to take
	if board.turn == color:
		return False
	return are_more_attackers_than_defenders(board, piece)

# Is a piece attacked and not defended
# Todo: Delete?
def is_free_to_take2(board, piece):
	color = board.color_at(piece)
	# e.g. if it's white's turn, a white piece cannot be free to take
	if board.turn == color:
		return False
	defenders = board.attackers(color, piece)
	attackers = board.attackers(not color, piece)
	# attacked by non-pinned color and (not defended by not color or defended only by pinned pieces)
	if attackers and (not all([board.is_pinned(color, attacker) for attacker in attackers])) \
		and (not defenders or (all([board.is_pinned(not color, defender) for defender in defenders]))):
		return True
	return False

# What is the most valuable piece that can be captured
# Returns square of most valuable free to take piece
def get_most_valuable_free_to_take(board):
	for piece_type in MOST_VALUABLE_TO_LEAST_PIECE_TYPES:
		pieces = board.pieces(piece_type, not board.turn)
		for piece in pieces:
			if is_free_to_take(board, piece):
				return piece
	return None

# Is the defended piece being attacked by something of lesser value
# Returns the value of the piece being won after the trade, the weakest attacking piece
# Does not check whose turn it is
def get_trade_value(board, piece):
	color = board.color_at(piece)
	# attacked by color and defended by not color
	if board.is_attacked_by(not color, piece) and board.is_attacked_by(color, piece):
		attackers = [attacker for attacker in board.attackers(not color, piece) if can_piece_capture(board, attacker, piece)]
		min_attacker_value = PIECE_TYPES_TO_VALUES[chess.QUEEN]
		is_lesser_value_attacker = False
		piece_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(piece)]
		for attacker in attackers:
			if board.piece_type_at(attacker) != chess.KING:
				attacker_value = PIECE_TYPES_TO_VALUES[board.piece_type_at(attacker)]
				if attacker_value + 100 < piece_value:
					min_attacker_value = min(min_attacker_value, attacker_value)
					is_lesser_value_attacker = True
		if is_lesser_value_attacker:
			return min_attacker_value
	return 0

# Is the defended piece being attacked by something of lesser value
# Returns (piece, value) - the piece getting taken and the value of the piece being won after the trade, the weakest attacking piece
# 	So if a pawn is attacking a knight, the value of the pawn is returned
# Todo: Need to fix this up. Only checking if pieces are attacked
def get_most_valuable_free_to_trade(board):
	good_trade_piece_types = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
	most_valuable_piece = None
	# Value of the second piece being lost in the trade
	highest_trade_value = 0
	# Value of the material difference being won in the trade
	highest_value_won = 0
	for piece_type in good_trade_piece_types:
		pieces = board.pieces(piece_type, not board.turn)
		for piece in pieces:
			trade_value = get_trade_value(board, piece)
			if trade_value > 0: # There is a trade available
				value_won = PIECE_TYPES_TO_VALUES[piece_type] - trade_value
				if value_won > highest_value_won:
					most_valuable_piece = piece
					highest_trade_value = trade_value
					highest_value_won = value_won
	return most_valuable_piece, highest_trade_value

# Is the game a draw
# Treats 50 move rule and 3-fold repetition as a draw even though that is not necessarily the case
def is_draw(board):
	return board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves() or board.is_repetition()

def is_or_can_claim_draw(board):
	return board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw()

# Lichess ends the game after the fifty move rule as well as three-fold repetition Todo: This is not guaranteed; it is based on user preference
def is_game_over(board):
	return board.is_game_over() or board.is_fifty_moves() or board.is_repetition()

