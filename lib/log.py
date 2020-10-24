import time

logfile = 'log.dat'

def l(msg):
	global logfile

	fh = open(logfile, 'a')
	fh.write('%s %s\n' % (time.asctime(), msg))
	fh.close()

def set_l(file_):
	global logfile

	logfile = file_
