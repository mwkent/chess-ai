#TODO: Value quicker mates
#import lib
#from lib import position_evaluator
import position_evaluator
import datetime
import time
from transposition_table import tt_init, tt_lookup_helper, tt_store

node_count = 0
prune_count = 0
tt_hit_count = 0

def minimax_helper(board, depth, use_tt=False, sort_moves=False):
	start = datetime.datetime.now()
	turn = board.turn
	result = minimax(board, depth, turn, position_evaluator.MIN_EVAL, position_evaluator.MAX_EVAL, use_tt, sort_moves)
	print("result = ", result)
	global prune_count, node_count, tt_hit_count
	print("prune_count = ", prune_count)
	print("node_count = ", node_count)
	if use_tt:
		print("tt_hit_count = ", tt_hit_count)
	end = datetime.datetime.now()
	print("move time = ", end-start)
	return result

# alpha is the min possible value
# beta is the max possible value
def minimax(board, depth, turn, alpha, beta, use_tt=False, sort_moves=False):
	global node_count, prune_count, tt_hit_count
	node_count += 1
	if depth == 0 or board.is_game_over():
		evaluation = (position_evaluator.evaluate_position(board, turn), board.peek())
		#print("depth = ", depth)
		#print("leaf evaluation = ", evaluation)
		#print(board)
		return evaluation
	if use_tt:
		tt_hit = tt_lookup_helper(board, alpha, beta, depth, turn)
		if tt_hit and tt_hit[0]:
			tt_hit_count += 1
			return tt_hit[1]
	moves = list(board.legal_moves)
	if (sort_moves):
		moves = sorted(moves, reverse = True, key = lambda move: get_move_value(board, turn, move))
	maximizing = board.turn == turn
	if maximizing:
		# Set to first legal move in case all evaluations are losing
		max_evaluation = (position_evaluator.MIN_EVAL, moves[0])
		for move in moves:
			board.push(move)
			evaluation = minimax(board, depth - 1, turn, alpha, beta, use_tt, sort_moves)
			board.pop()
			if evaluation[0] > max_evaluation[0]: # greater than so max_evaluation only gets replaced if evaluation is higher
			# that way max_evaluation will only be updated with a fully evaluated node
				max_evaluation = (evaluation[0], move)
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
	# Else
	# Set to first legal move in case all evaluations are losing
	min_evaluation = (position_evaluator.MAX_EVAL, moves[0])
	for move in moves:
		board.push(move)
		evaluation = minimax(board, depth - 1, turn, alpha, beta, use_tt, sort_moves)
		board.pop()
		if evaluation[0] < min_evaluation[0]:
			min_evaluation = (evaluation[0], move)
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

def get_move_value(board, turn, move):
	board.push(move)
	evaluation = position_evaluator.evaluate_position(board, turn)
	board.pop()
	return evaluation

def init_counts():
	global node_count, prune_count, tt_hit_count
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
def pick_full_move_with_tt(board, depth=3):
	init_counts()
	num_elements = 1024 * 8
	tt_init(num_elements)
	result = minimax_helper(board, depth, sort_moves=True, use_tt=True)
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

