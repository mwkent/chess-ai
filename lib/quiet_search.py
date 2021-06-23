import chess
import chess_util
import position_evaluator


PIECE_TYPES_TO_VALUES = position_evaluator.PIECE_TYPES_TO_VALUES.copy()
PIECE_TYPES_TO_VALUES[chess.KING] = 0

quiet_node_count = 0


# Returns evaluation, node_count; evaluation is based on turn; positive if good for turn, negative if not good for turn
def quiet_search_helper2(board, turn, evaluate_position=position_evaluator.evaluate_position, sort_moves=True):
	global quiet_node_count
	quiet_node_count = 0
	score, _ = quiet_search2(board)
	if turn != board.turn:
		score = -score
	return score, quiet_node_count

# Returns evaluation after checking all possible captures
# Quiescence Search
# alpha is the min possible value
# beta is the max possible value
# num_checks is the number of checks to search
# Returns (evaluation, depth_reached) where evaluation is based on board.turn
# Todo: Evaluate position in a simpler fashion
def quiet_search2(board, alpha=position_evaluator.MIN_EVAL, beta=position_evaluator.MAX_EVAL, \
	evaluate_position=position_evaluator.evaluate_position, sort_moves=True, num_checks=1, depth=10, depth_reached=0):
	global quiet_node_count
	quiet_node_count += 1
	if depth == 0 or chess_util.is_game_over(board):
		evaluation = evaluate_position(board, board.turn)
		if evaluation >= beta:
			return beta, -1
		if evaluation > alpha:
			alpha = evaluation
		return alpha, depth_reached
	if board.is_check():
		moves = board.legal_moves
		if sort_moves:
			moves = sorted(moves, reverse = True, key = lambda move: get_mvv_lva_value(board, move))
		for move in moves:
			board.push(move)
			evaluation, sub_depth_reached = quiet_search2(board, -beta, -alpha, evaluate_position, num_checks=num_checks, depth=depth-1)
			evaluation = -evaluation
			board.pop()

			if evaluation >= beta:
				return beta, -1
			if evaluation > alpha:
			   alpha = evaluation
		return alpha, sub_depth_reached

	evaluation = evaluate_position(board, board.turn)
#	print()
#	print(board.move_stack)
#	print(board)
#	print("alpha =", alpha)
#	print("beta =", beta)
#	print("evaluation =", evaluation)
	if evaluation >= beta:
		return beta, -1
	if evaluation > alpha:
		alpha = evaluation
	moves = [move for move in board.legal_moves if board.is_capture(move) or (num_checks > 0 and board.gives_check(move))]
	if not moves:
		return alpha, depth_reached
	if sort_moves:
		moves = sorted(moves, reverse = True, key = lambda move: get_mvv_lva_value(board, move))
	for move in moves:
		num_remaining_checks = num_checks
		if not board.is_capture(move) and board.gives_check(move):
			num_remaining_checks = num_checks - 1
		board.push(move)
		evaluation, sub_depth_reached = quiet_search2(board, -beta, -alpha, evaluate_position, num_checks=num_remaining_checks, depth=depth-1)
		evaluation = -evaluation
		board.pop()

		if evaluation >= beta:
			return beta, -1
		if evaluation > alpha:
		   alpha = evaluation
	return alpha, sub_depth_reached

def quiet_search_helper(board, turn, evaluate_position=position_evaluator.evaluate_position, sort_moves=True):
	global quiet_node_count
	quiet_node_count = 0
	score, _ = quiet_search(board)
	if turn != board.turn:
		score = -score
	return score, quiet_node_count

# Uses simpler position evaluation
def quiet_search(board, old_evaluation=None, alpha=position_evaluator.MIN_EVAL, beta=position_evaluator.MAX_EVAL, \
	evaluate_position=position_evaluator.evaluate_position_after_capture, sort_moves=True, num_checks=1, depth=6, depth_reached=0):
	global quiet_node_count
	quiet_node_count += 1
	evaluation = evaluate_position(board, board.turn, old_evaluation)

	#print()
	#print(board.move_stack)
	#print(board)
	#print("depth =", depth)
	#print("alpha =", alpha)
	#print("beta =", beta)
	#print("old evaluation =", old_evaluation)
	#print("evaluation =", evaluation)

	if depth == 0 or chess_util.is_game_over(board):
		if evaluation >= beta:
			return beta, -1
		if evaluation > alpha:
			alpha = evaluation
		return alpha, depth_reached

#	print("before is check")
	# Consider all legal moves when in check
	if board.is_check():
		moves = board.legal_moves
		if sort_moves:
			moves = sorted(moves, reverse = True, key = lambda move: get_mvv_lva_value(board, move))
		for move in moves:
			board.push(move)
			sub_evaluation, sub_depth_reached = quiet_search(board, evaluation, -beta, -alpha, evaluate_position, num_checks=num_checks, depth=depth-1)
			sub_evaluation = -sub_evaluation
			board.pop()

			if sub_evaluation >= beta:
				return beta, -1
			if sub_evaluation > alpha:
			   alpha = sub_evaluation
		return alpha, sub_depth_reached

	if evaluation >= beta:
		return beta, -1
	if evaluation > alpha:
		alpha = evaluation
	moves = [move for move in board.legal_moves if board.is_capture(move) or (num_checks > 0 and board.gives_check(move))]
	if not moves:
		return alpha, depth_reached
	if sort_moves:
		moves = sorted(moves, reverse = True, key = lambda move: get_mvv_lva_value(board, move))
	for move in moves:
		num_remaining_checks = num_checks
		if not board.is_capture(move) and board.gives_check(move):
			num_remaining_checks = num_checks - 1
		board.push(move)
		sub_evaluation, sub_depth_reached = quiet_search(board, evaluation, -beta, -alpha, evaluate_position, num_checks=num_remaining_checks, depth=depth-1)
		sub_evaluation = -sub_evaluation
		board.pop()

		if sub_evaluation >= beta:
			return beta, -1
		if sub_evaluation > alpha:
		   alpha = sub_evaluation
	return alpha, sub_depth_reached

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

