# This file was used to generate brown_freq.py
# Unigram frequencies of Brown Corpus

import nltk
import re
from nltk.corpus import brown
from collections import Counter

words = Counter()

for sentence in brown.sents():
    for word in sentence:
        words[(word.lower())] += 1

for k,v in words.most_common():
    if len(k) and re.search('[a-z]', k): #only print alpha-words
        print(k,v,sep='\t')

