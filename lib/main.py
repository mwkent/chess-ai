# Runs engine

import uci
import sys
from log import set_l


if len(sys.argv) == 2:
	set_l(sys.argv[1])

uci.main()
