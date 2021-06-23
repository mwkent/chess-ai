# Todo: Value quicker mates
# Todo: Consider extensions. Extend depth on certain positions (e.g., checks, hanging pieces)
# Todo: Add checks to quiet_search
# Todo: Check late move reduction
# Todo: Negamax? Is it any faster than minimax?
# Todo: Rewrite some code in c++; c++ 100x faster?
# Todo: Update quiet_search to check for draws by repition as well. Need some way to stop draw by repetition at depth of only 1
# Todo: Move quiet_search to own file
import chess
import chess_util
import position_evaluator
import quiet_search as qs
import datetime
import time
from transposition_table2 import tt_init, tt_lookup_helper, tt_store

# Mate in 2 is worse than mate in 1
MATE_DEPTH_PENALTY = 1
PIECE_TYPES_TO_VALUES = position_evaluator.PIECE_TYPES_TO_VALUES.copy()
PIECE_TYPES_TO_VALUES[chess.KING] = 0

quiet_node_count = 0
node_count = 0
prune_count = 0
tt_hit_count = 0

# Returns (evaluation, move)
# This is a wrapper around minimax to cover anything required before the search starts
# Don't need to pass in alpha and beta like in minimax
def minimax_helper(board, depth, use_tt=False, sort_moves=False, evaluate_position=position_evaluator.evaluate_position, use_quiet_search=False):
	start = datetime.datetime.now()
	turn = board.turn
	result = minimax(board, depth, turn, position_evaluator.MIN_EVAL, position_evaluator.MAX_EVAL, \
		evaluate_position, use_quiet_search, use_tt, sort_moves)
	print("depth =", depth)
	print("result = ", result)
	global prune_count, quiet_node_count, node_count, tt_hit_count
	print("prune_count = ", prune_count)
	print("node_count = ", node_count)
	if use_quiet_search:
		print("quiet_node_count = ", quiet_node_count)
	if use_tt:
		print("tt_hit_count = ", tt_hit_count)
	end = datetime.datetime.now()
	print("move time = ", end-start)
	return (result[0], result[1][0])

# Returns (evaluation, move list)
# alpha is the min possible value
# beta is the max possible value
def minimax(board, depth, turn, alpha, beta, evaluate_position, use_quiet_search, use_tt=False, sort_moves=False, depth_reached=0):
	global node_count, prune_count, tt_hit_count, quiet_node_count
	node_count += 1
	if depth == 0 or chess_util.is_game_over(board):
		evaluation = 0
		if use_quiet_search:
			score, quiet_node_count = qs.quiet_search_helper(board, turn)
			evaluation = (score, board.peek())
		else:
			evaluation = (evaluate_position(board, turn), [])
		#print("depth = ", depth)
		#print("leaf evaluation = ", evaluation)
		#print("is game over =", board.is_game_over(claim_draw=True))
		#print("is repitition =", board.is_repetition())
		#print(board)
		#print(board.move_stack)
		return evaluation
	if use_tt:
		tt_hit = tt_lookup_helper(board, alpha, beta, depth, turn)
		if tt_hit and tt_hit[0]:
			tt_hit_count += 1
			return tt_hit[1]
	moves = list(board.legal_moves)
	if (sort_moves):
		moves = sorted(moves, reverse = True, key = lambda move: get_move_value(board, turn, move, evaluate_position))
	maximizing = board.turn == turn
	if maximizing:
		max_evaluation = None
		for move in moves:
			board.push(move)
			evaluation = minimax(board, depth - 1, turn, alpha, beta, evaluate_position, use_quiet_search, use_tt, sort_moves)
			board.pop()
			if max_evaluation == None or evaluation[0] > max_evaluation[0]: # greater than so max_evaluation only gets replaced if evaluation is higher
			# that way max_evaluation will only be updated with a fully evaluated node
				max_evaluation = (evaluation[0], [move] + evaluation[1])
			alpha = max(alpha, max_evaluation[0])
			if beta <= alpha: #less than or equal to and break, should return first best solution because it is fully evaluated
			# Remaining nodes could have a worse evaluation, so do not replace prior best solution
				prune_count += 1
				break
		#print("depth = ", depth)
		#print("max_evaluation = ", max_evaluation)
		#print(board)
		if use_tt:
			tt_store(board, alpha, beta, max_evaluation[0], max_evaluation[1], depth, turn)
		return max_evaluation
	# Else minimizing
	min_evaluation = None
	for move in moves:
		board.push(move)
		evaluation = minimax(board, depth - 1, turn, alpha, beta, evaluate_position, use_quiet_search, use_tt, sort_moves)
		board.pop()
		if min_evaluation == None or evaluation[0] < min_evaluation[0]:
			min_evaluation = (evaluation[0], [move] + evaluation[1])
		beta = min(beta, min_evaluation[0])
		if beta <= alpha:
			prune_count += 1
			break
	#print("depth = ", depth)
	#print("min_evaluation = ", min_evaluation)
	#print(board)
	if use_tt:
		tt_store(board, alpha, beta, min_evaluation[0], min_evaluation[1], depth, turn)
	return min_evaluation

# Todo: Test and use this
# Handles mate in 1 is better than mate in 2
def get_evaluation(board, turn, evaluate_position, use_quiet_search, depth_reached):
	evaluation = 0
	if use_quiet_search:
		score, quiet_depth_reached = qs.quiet_search_helper(board, turn)
		score = get_mate_depth_adjusted_eval(score, depth_reached + quiet_depth_reached)
		evaluation = (score, board.peek())
	else:
		score = evaluate_position(board, turn)
		score = get_mate_depth_adjusted_eval(score, depth_reached)
		evaluation = (score, board.peek())
	return evaluation

def get_mate_depth_adjusted_eval(score, depth_reached):
	return score - depth_reached * MATE_DEPTH_PENALTY if score == position_evaluator.MAX_EVAL else score


# Returns evaluation based on turn; positive if good for turn, negative if not good for turn
def quiet_search_helper2(board, turn, evaluate_position=position_evaluator.evaluate_position, sort_moves=True):
	score, _ = quiet_search2(board)
	return score if turn == board.turn else -score

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
	score, _ = quiet_search(board)
	return score if turn == board.turn else -score

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

def get_move_value(board, turn, move, evaluate_position):
	board.push(move)
	evaluation = evaluate_position(board, turn)
	board.pop()
	return evaluation

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

def init_counts():
	global quiet_node_count, node_count, prune_count, tt_hit_count
	quiet_node_count = 0
	node_count = 0
	prune_count = 0
	tt_hit_count = 0

# Minimax with alpha beta pruning to some depth
def pick_full_move(board, depth=3):
	init_counts()
	result = minimax_helper(board, depth)
	return result

# Minimax with alpha beta pruning to some depth
def pick_move(board, depth=3):
	return pick_full_move(board, depth)[1]

# Sort moves to facilitate more pruning
def pick_full_move_with_sort(board, depth=3):
	init_counts()
	result = minimax_helper(board, depth, sort_moves=True)
	return result

def pick_move_with_sort(board, depth=3):
	return pick_full_move_with_sort(board, depth)[1]

# transposition table
# Initializes tt every move search?
def pick_full_move_with_tt(board, depth=3):
	init_counts()
	num_elements = 1024 * 8
	tt_init(num_elements)
	result = minimax_helper(board, depth, sort_moves=False, use_tt=True)
	return result

def pick_move_with_tt(board, depth=3):
	return pick_full_move_with_tt(board, depth)[1]

# Iterative deepening search
def pick_move_ids(board, max_depth=3):
	init_counts()
	result = (position_evaluator.MIN_EVAL, None)
	depth = 1
	while(depth <= max_depth and result[0] < position_evaluator.MAX_EVAL):
		result = minimax_helper(board, depth)
		depth += 1
	return result[1]

# Iterative deepening search with transposition table
def pick_move_ids_with_tt(board, max_depth=3):
	init_counts()
	num_elements = 1024 * 8
	tt_init(num_elements)
	result = (position_evaluator.MIN_EVAL, None)
	depth = 1
	while(depth <= max_depth and result[0] < position_evaluator.MAX_EVAL):
		result = minimax_helper(board, depth, use_tt=True)
		depth += 1
	return result[1]

# Iterative deepening search within time limit
def pick_move_in_time(board, time_in_seconds=1):
	init_counts()
	start = time.time()
	elapsed_time = 0
	result = (position_evaluator.MIN_EVAL, None)
	depth = 1
	while(elapsed_time < time_in_seconds and result[0] < position_evaluator.MAX_EVAL):
		result = minimax_helper(board, depth)
		depth += 1
		#end = datetime.datetime.now()
		end = time.time()
		elapsed_time = end - start
		print("elapsed_time =", elapsed_time)
	print("depth =", depth-1)
	return result[1]

# Iterative deepening search within time limit
def pick_full_move_in_time(board, time_in_seconds=1):
	init_counts()
	start = time.time()
	elapsed_time = 0
	result = (position_evaluator.MIN_EVAL, None)
	depth = 1
	while(elapsed_time < time_in_seconds and result[0] < position_evaluator.MAX_EVAL):
		result = minimax_helper(board, depth)
		depth += 1
		#end = datetime.datetime.now()
		end = time.time()
		elapsed_time = end - start
		print("elapsed_time =", elapsed_time)
	print("depth =", depth-1)
	result = [result[0], result[1], depth, elapsed_time]
	return result

