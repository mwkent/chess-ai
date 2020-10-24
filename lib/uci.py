# Handles UCI (Universal Chess Interface)
# See UCI protocol: http://wbec-ridderkerk.nl/html/UCIProtocol.html

from board import Board
import chess
import chess.polyglot
import math
from multiprocessing import Queue
from select import select
import sys
import threading
from threading import Thread
import time
import traceback
from brain import calc_move, cm_thread_start, cm_thread_check, cm_thread_stop
from log import set_l, l

ponder = False
benchmark = False
epd = False

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

def perft(board, depth):
    if depth == 1:
        return board.move_count()

    total = 0

    for m in board.get_move_list():
        board.push(m)
        total += perft(board, depth - 1)
        board.pop()

    return total

def send(str_):
    print(str_)
    l('OUT: %s' % str_)
    sys.stdout.flush()

def wait_init_thread(t):
    if not t:
        return

    send('info string waiting for init thread')

    t.join()

    send('info string initialized')

    return None

def uci():
    send('id name abc')
    send('id author matt')
    send('uciok')

def is_ready():
    send('readyok')

def uci_new_game():
    board = Board()
    cm_thread_stop()

def position(parts, board):
    is_moves = False
    nr = 1
    while nr < len(parts):
        if is_moves:
            board.push_uci(parts[nr])

        elif parts[nr] ==  'fen':
            if "moves" in parts:
                board = Board(" ".join(parts[nr + 1:nr + 7])) # should not overshadow board
                nr += 6
            else:
                board = Board(" ".join(parts[nr + 1:]))
                break

        elif parts[nr] == 'startpos':
            board.reset()

        elif parts[nr] == 'moves':
            is_moves = True

        else:
            l('unknown: %s' % parts[nr])

        nr += 1

def go(t, parts, board, sr):
    t = wait_init_thread(t)
    if cm_thread_stop():
        l('stop pondering')

    movetime = None
    depth = None
    wtime = btime = None
    winc = binc = 0
    movestogo = None

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

        else:
            l('unknown: %s' % parts[nr])

        nr += 1

    ###
    current_duration = movetime

    if current_duration:
        current_duration = float(current_duration) / 1000.0

    elif wtime and btime:
        ms = wtime
        time_inc = winc
        if not board.turn:
            ms = btime
            time_inc = binc

        ms /= 1000.0
        time_inc /= 1000.0

        if movestogo == None:
            movestogo = 40 - board.fullmove_number
            while movestogo < 0:
                movestogo += 40

        current_duration = (ms + movestogo * time_inc) / (board.fullmove_number + 7);

        limit_duration = ms / 15.0
        if current_duration > limit_duration:
            current_duration = limit_duration

        if current_duration == 0:
            current_duration = 0.001

        l('mtg %d, ms %f, ti %f' % (movestogo, ms, time_inc))
    ###
    if current_duration:
        l('search for %f seconds' % current_duration)

    if depth == None:
        depth = 10

    cm_thread_start(board, current_duration, depth, False)

    line = None
    while cm_thread_check():
        line = sr.get(0.01)

        if line:
            line = line.rstrip('\n')

            if line == 'stop' or line == 'quit':
                break

    result = cm_thread_stop()

    if line == 'quit':
        return

    if result and result[1]:
        send('bestmove %s' % result[1].uci())
        board.push(result[1])

    else:
        # Throw exception
        send('bestmove a1a1')

def fen(board):
    send('%s' % board.fen())

def eval_command(board, parts, t):
    moves = pc_to_list(board, [])

    depth = None
    if parts[0] == 'deval':
        t = wait_init_thread(t)
        depth = int(parts[1])
    elif len(parts) == 2:
        check_move = chess.Move.from_uci(parts[1])

    send('move\teval\tsort score')
    for m in moves:
        if not m.move == check_move:
            continue

        board.push(m.move)

        if depth:
            rc = calc_move(board, None, depth)
            v = rc[0]
            send('%s\t%d\t%d (%s)' % (m.move, v, m.score, rc[1]))

        else:
            v = evaluate(board)
            if board.turn == chess.BLACK:
                v = -v
            send('%s\t%d\t%d' % (m.move, v, m.score))

        board.pop()


def main():
    t = threading.Thread()
    t.start()

    try:
        sr = stdin_reader()
        sr.daemon = True
        sr.start()

        board = Board()

        while True:
            line = sr.get()
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

            elif parts[0] == 'ucinewgame':
                uci_new_game()

            elif parts[0] == 'perft': # Not in UCI protocol
                perft()

            elif parts[0] == 'position':
                position(parts, board)

            elif parts[0] == 'go':
                go(t, parts, board, sr)

            elif parts[0] == 'quit':
                break

            elif parts[0] == 'fen':
                fen(board)

            elif parts[0] == 'eval' or parts[0] == 'deval':
                eval_command(board, parts, t)

            elif parts[0] == 'moves':
                send('%s' % [m.uci() for m in board.get_move_list()])

            elif parts[0] == 'smoves':
                moves = board.get_move_list()
                send('%s' % [m.move.uci() for m in moves])

            elif parts[0] == 'trymovedepth':
                t = wait_init_thread(t)
                board.push(chess.Move.from_uci(parts[1]))
                send('%s' % calc_move(board, None, int(parts[2])))
                board.pop()

            else:
                l('unknown: %s' % parts[0])
                send('Unknown command')

                sys.stdout.flush()

        cm_thread_stop()

    except KeyboardInterrupt as ki:
        l('ctrl+c pressed')
        cm_thread_stop()

    except Exception as ex:
        l(str(ex))
        l(traceback.format_exc())

def benchmark_test():
    board = Board()
    calc_move(board, 60.0, 999999)

def epd_test(str_):
    parts = str_.split(';')
    board = chess.Board(parts[0])

    print(parts[0])

    for test in parts:
        test = test.strip()

        if test[0] != 'D':
            continue

        pparts = test.split(' ')

        depth = int(pparts[0][1:])

        count = int(pparts[1])

        verify = perft(board, depth)

        print('\t', depth, verify, count,)
        if verify == count:
            print('ok')
        else:
            print('FAIL!')
            sys.exit(1)

if len(sys.argv) == 2:
    set_l(sys.argv[1])

if benchmark:
    import cProfile
    cProfile.run('benchmark_test()', 'restats')
elif epd:
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        if len(line) == 0 or line[0] == '#':
            continue

        epd_test(line)
else:
    main()
