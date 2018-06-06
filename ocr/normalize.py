#!/usr/bin/python3

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
    step5 = step4.replace(" '", "'").replace(" n't", "n't").replace("can not", "cannot")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()

def charSubstitute(line):
    """
    Standardize common characters.
    """
    subs = {
        '’': "'",
        '‘': "'",
        '”': '"',
        '“': '"',
        'ﬂ': "fl",
        "ﬁ": "fi",
        '—': '--'
    }
    if line.endswith('—'):
        line = re.sub('—$', '-', line)
    for before, after in subs.items():
        line = line.replace(before, after)
    return line


for line in sys.stdin:
    line = line.strip()
    retokenized = untokenize(nltk.word_tokenize(charSubstitute(line)))
    print(retokenized)
