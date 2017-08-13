#!/usr/bin/python3

import sys
import os
import fileinput

fnames = fileinput.input() if len(sys.argv) < 2 else sys.argv[1:]
for fname in fnames:
    print(os.path.splitext(fname)[0])
