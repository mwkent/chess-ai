# Handles UCI (Universal Chess Interface)
# See UCI protocol: http://wbec-ridderkerk.nl/html/UCIProtocol.html

from chess import Board
from multiprocessing import Queue
import sys
import threading
import time
import traceback
import move_calculator
import think_time_calculator
from log import set_l, l

ponder = False

class stdin_reader(threading.Thread):
	q = Queue()

	def run(self):
		l('stdin thread started')

		while True:
			line = sys.stdin.readline()

			self.q.put(line)

		l('stdin thread terminating')

	def get(self, to = None):
		try:
			if not to:
				return self.q.get()

			return self.q.get(True, to)

		# FIXME except Queue.Empty as qe:
		except:
			return None

def send(str_):
	print(str_)
	l('OUT: %s' % str_)
	sys.stdout.flush()

def uci():
	send('id name FENder_Bender')
	send('id author Matt')
	send('uciok')

def is_ready():
	send('readyok')

# Todo: Implement
def set_option():
	pass

def uci_new_game():
	# Nothing is required, at this point, to start a new UCI game
	pass

# Is setting the position by playing the entire game slow?
def position(parts, board):
	is_moves = False
	nr = 1
	start_time = time.time()
	while nr < len(parts):
		if is_moves:
			board.push_uci(parts[nr])

		elif parts[nr] ==  'fen':
			if "moves" in parts:
				board.set_fen(" ".join(parts[nr + 1:nr + 7]))
				nr += 6
			else:
				board.set_fen(" ".join(parts[nr + 1:]))
				break

		elif parts[nr] == 'startpos':
			board.reset()

		elif parts[nr] == 'moves':
			is_moves = True

		else:
			l('unknown: %s' % parts[nr])

		nr += 1
	elapsed_time = time.time() - start_time
	print("time to set position =", elapsed_time)

def go(parts, board):
	movetime = None
	depth = None
	wtime = btime = None
	winc = binc = 0
	movestogo = None
	ponder = False
	ponder_move = None

	nr = 1
	while nr < len(parts):
		if parts[nr] == 'wtime':
			wtime = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'btime':
			btime = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'winc':
			winc = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'binc':
			binc = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'movetime':
			movetime = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'movestogo':
			movestogo = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'depth':
			depth = int(parts[nr + 1])
			nr += 1

		elif parts[nr] == 'ponder':
			ponder = True
			ponder_move = int(parts[nr + 1])
			nr += 1

		else:
			l('unknown: %s' % parts[nr])

		nr += 1

	###
	current_duration = movetime

	if current_duration:
		current_duration = float(current_duration) / 1000.0

	elif wtime and btime:
		current_duration = think_time_calculator.get_max_think_time(board, wtime, winc, btime, binc)

	if current_duration:
		l('search for %f seconds' % current_duration)

	if depth == None:
		depth = 10

	result = move_calculator.calculate(board, current_duration, depth, is_ponder=ponder)

	if result and result[1]:
		send('bestmove %s' % result[1].uci())
		board.push(result[1])

	else:
		# Throw exception
		print("ERROR getting move")
		send('bestmove a1a1')

def fen(board):
	send('%s' % board.fen())

def main():
	try:
		reader = stdin_reader()
		reader.daemon = True
		reader.start()

		board = Board()

		while True:
			line = reader.get()
			if line == None:
				break

			line = line.rstrip('\n')

			if len(line) == 0:
				continue

			l('IN: %s' % line)

			parts = line.split(' ')

			if parts[0] == 'uci':
				uci()

			elif parts[0] == 'isready':
				is_ready()

			elif parts[0] == 'setoption':
				set_option()

			elif parts[0] == 'ucinewgame':
				uci_new_game()
				board = Board()

			elif parts[0] == 'position':
				position(parts, board)

			elif parts[0] == 'go':
				go(parts, board)

			elif parts[0] == 'quit':
				break

			elif parts[0] == 'fen':
				fen(board)

			else:
				send("Unknown command =%s" % parts[0])

				sys.stdout.flush()

	except KeyboardInterrupt:
		l('ctrl+c pressed')

	except Exception as ex:
		send(ex)
		l(str(ex))
		l(traceback.format_exc())

if len(sys.argv) == 2:
	set_l(sys.argv[1])

main()
