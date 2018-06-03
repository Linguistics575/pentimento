#!/usr/bin/python3

import sys
import re

endswithpunctuation = pagebreak = paragraphbreak = False
text = [[]]
for line in sys.stdin:
    line = line.strip()
    if line.startswith('Introduction.') or line.endswith('Egypt as a Winter Resort.') or len(line) == 1:
        pagebreak = True
    elif len(line) == 0:
        paragraphbreak = True
    else:
        if paragraphbreak and (not pagebreak or endswithpunctuation):
            text.append([])
        endswithpunctuation = re.search('[.?!]$', line) is not None
        pagebreak = False
        paragraphbreak = False
        text[-1].append(line)

for paragraph in text:
    print(' '.join(paragraph))
