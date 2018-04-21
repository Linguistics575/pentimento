#!/usr/bin/python3

import sys
import re
from collections import Counter

c = Counter()
for line in sys.stdin:
    c.update(re.split('[_():,.–/;&!]', line.strip().lower()))

for k,v in c.most_common():
    if len(k) and re.search('[a-z]', k): #only print alpha-words
        print(k,v,sep='\t')
