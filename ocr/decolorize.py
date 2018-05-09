#!/usr/bin/python3

import sys

def remove(s, badsubstrs):
    for substr in badsubstrs:
        s = s.replace(substr, '')
    return s

colorchars = {'\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m', '\033[4m',}

for c in colorchars:
    print(len(c))

for line in sys.stdin:
    print(remove(line.rstrip(), colorchars))
