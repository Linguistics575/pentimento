#!/usr/bin/python3

from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer
import sys
import nltk

import re
def untokenize(words):
    """
    Untokenizing a text undoes the tokenizing operation, restoring
    punctuation and spaces to the places that people expect them to be.
    Ideally, `untokenize(tokenize(text))` should be identical to `text`,
    except for line breaks.
    """
    text = ' ' + ' '.join(words) + ' '
    step1 = text.replace("`` ", '"').replace(" ''", '"').replace('. . .',  '...').replace(" -- ", "--")
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`)])', r"\1\2", step2)
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`)])', r"\1\2", step3)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace(
         "can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()


tokenizer = MosesTokenizer()
detokenizer = MosesDetokenizer()

for line in sys.stdin:
    line = line.strip()
    retokenized = untokenize(nltk.word_tokenize(line.replace('‘', "'").replace('’', "'").replace('”', '"').replace('“', '"')))
    
    if line != retokenized:
        print(line)
        print(retokenized)
