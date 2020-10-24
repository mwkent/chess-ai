import chess
import position_evaluator
import datetime

node_count = 0

def minimax(board, depth, turn):
	global node_count
	node_count += 1
	if depth == 0 or board.is_game_over():
		if depth != 0:
			print("Game is over, but depth is not 0.")
		evaluation = (position_evaluator.evaluate_position(board, turn), board.peek())
		print("depth =", depth)
		print("leaf evaluation =", evaluation)
		print(board)
		return evaluation
	maximizing = board.turn == turn
	if maximizing:
		max_evaluation = (position_evaluator.MIN_EVAL, None)
		for move in board.legal_moves:
			board.push(move)
			evaluation = minimax(board, depth - 1, turn)
			if evaluation[0] >= max_evaluation[0]:
				max_evaluation = (evaluation[0], move)
			board.pop()
		print("depth =", depth)
		print("max_evaluation =", max_evaluation)
		print(board)
		return max_evaluation
	# Else
	min_evaluation = (position_evaluator.MAX_EVAL, None)
	for move in board.legal_moves:
		board.push(move)
		evaluation = minimax(board, depth - 1, turn)
		if evaluation[0] <= min_evaluation[0]:
			min_evaluation = (evaluation[0], move)
		board.pop()
	print("depth =", depth)
	print("min_evaluation =", min_evaluation)
	print(board)
	return min_evaluation


def pick_move(board, depth=3):
	start = datetime.datetime.now()
	turn = board.turn
	result = minimax(board, depth, turn)
	print("result =", result)
	print("node_count =", node_count)
	end = datetime.datetime.now()
	print("move time =", end-start)
	return result[1]

