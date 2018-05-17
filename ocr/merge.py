#!/usr/bin/python3

import sys
import difflib
import nltk
import re
import os
from PorterStemmer import PorterStemmer
from collections import Counter

p = PorterStemmer()
wikiwords = set([line.split('\t')[0] for line in open('../WikipediaTitles/titleWordCount.tsv')])
words = set([line.strip() for line in open('../spellchecker/words.txt').readlines()])
lemmas = set([p.stem(word, 0, len(word)-1) for word in words])
words.update([line.strip() for line in open('romannumerals.txt')])
debug = None
html = False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class hcolors: #same as bcolors, but html
    HEADER = '<span style="color: #73299e;">'
    OKBLUE = '<span style="color: #0000FF;">'
    OKGREEN = '<span style="color: #00FF00;">'
    WARNING = '<span style="color: #d6c720;">'
    FAIL = '<span style="color: #ff0000;">'
    ENDC = '</span>'
    BOLD = '<span style="font-weight:bold">'
    UNDERLINE = '<span style="text-decoration: underline;">'

def blue(text):
    klass = hcolors if html else bcolors
    return klass.OKBLUE + text + klass.ENDC

def yellow(text):
    klass = hcolors if html else bcolors
    return klass.WARNING + text + klass.ENDC

def red(text):
    klass = hcolors if html else bcolors
    return klass.FAIL + text + klass.ENDC

def strike(text):
    result = ''
    for c in text:
        result = result + '\u0336' + c
    return result

class Token:
    def __init__(self, val, after, sourcedoc):
        self.val = val
        self.after = after
        self.repr = self.val + self.after
        self.sourcedoc = sourcedoc

def tokenize(filename):
    text = ''.join(open(filename).readlines()).replace('-\n', '').replace('``', '"').replace("''", '"')
    tokstrs = [s.replace('``', '"').replace("''", '"') for s in nltk.word_tokenize(text)]
    tokens = []
    chunkNumber = 0
    i = 0
    for line, afters in getLineTokens(text, tokstrs):
        if len(line) == 0 and len(tokens):
            tokens[-1].after += '\n'
            tokens[-1].repr += '\n'
        for tok,after in zip(line, afters):
            tokens.append(Token(tok, after, filename))
    return tokens

def markNonWords(seq):
    for word in seq:
        if not isMorphologicallyPlausable(word.val, words, True) and not isMorphologicallyPlausable(word.val, wikiwords, False):
            word.repr = red(word.val + word.after)


def mergeChunk(keep, reject, confident=True):
    for tok in keep:
        if confident:
            tok.repr = blue(tok.repr)
        else:
            tok.repr = red(tok.repr)
    for tok in reject:
        if confident and debug:
            tok.repr = yellow(strike(tok.repr))
        elif debug:
            tok.repr = red(strike(tok.repr))
        else:
            tok.repr = ''
        tok.val = ''
        tok.after = ''
    return [reject + keep]

def isMorphologicallyPlausable(word, dictionary, allowLemma=False):
    parts = re.split("['.-]", word)
    for elem in parts:
        if re.search(r'[a-zA-Z]', elem) and elem.lower() not in dictionary:
            if not (allowLemma and p.stem(elem.lower(), 0, len(elem)-1) in lemmas):
                return False
    return True

def areWords(seq, dictionary, allowLemma=False):
    for elem in seq:
        if re.search(r'[a-zA-Z]', elem.val) and not isMorphologicallyPlausable(elem.val, dictionary, allowLemma):
            return False
    return True

def mergeAlternateSpelling(seqa, seqb):
    for allowLemma in [False, True]:
        for dic in [words, wikiwords]:
            areWordsA = areWords(seqa, dic, allowLemma)
            areWordsB = areWords(seqb, dic, allowLemma)
            if areWordsA and not areWordsB:
                return mergeChunk(seqa, seqb)
            if not areWordsA and areWordsB:
                return mergeChunk(seqb, seqa)
    return [seqa, seqb]

def doSpellingMerge(mergeInfo):
    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            chunk = mergeAlternateSpelling(chunk[0], chunk[1])
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo

def isCorrectCapitalization(seq, prevToken):
    for prev,cur in zip([prevToken] + seq, seq):
        if prev.val == '.':
            if not cur.val[0].isupper():
                return False
        else:
            if cur.val not in words:
                return False
    return True

def mergeAlternateCapitalization(seqa, seqb, prevToken):
    stringa = ' '.join([s.val for s in seqa])
    stringb = ' '.join([s.val for s in seqb])
    if stringa.lower() == stringb.lower():
        aIsCorrect = isCorrectCapitalization(seqa, prevToken)
        bIsCorrect = isCorrectCapitalization(seqb, prevToken)
        if aIsCorrect and not bIsCorrect:
            return mergeChunk(seqa, seqb)
        if not aIsCorrect and bIsCorrect:
            return mergeChunk(seqb, seqa)
        if aIsCorrect and bIsCorrect:
            if stringa.islower():
                return mergeChunk(seqa, seqb)
            if stringb.islower():
                return mergeChunk(seqb, seqa)
    return [seqa, seqb]

def doCapitalizationMerge(mergeInfo):
    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            prevToken = None
            if len(revisedMergeInfo):
                prevToken = revisedMergeInfo[-1][0][-1]
            chunk = mergeAlternateCapitalization(chunk[0], chunk[1], prevToken)
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo

def mergeUnigramFrequency(seqa, seqb, wordFreq):
    areWordsA = areWords(seqa, words, True)
    areWordsB = areWords(seqb, words, True)
    if areWordsA and areWordsB and len(seqa) == len(seqb):
        aScore = 1
        bScore = 1
        for word in seqa:
            aScore *= (wordFreq.get(word.val.lower()) or 0)
        for word in seqb:
            bScore *= (wordFreq.get(word.val.lower()) or 0)
        if aScore > (bScore * 10):
            return mergeChunk(seqa, seqb)
        if bScore > (aScore * 10):
            return mergeChunk(seqb, seqa)
    return [seqa, seqb]

def doUnigramFrequncyMerge(mergeInfo, internalConfidentUnigrams):
    freqs = {s.split('\t')[0]: int(s.split('\t')[1]) for s in open('brown_freq.txt').readlines()}

    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            chunk = mergeUnigramFrequency(chunk[0], chunk[1], internalConfidentUnigrams)
        if len(chunk) == 2:
            chunk = mergeUnigramFrequency(chunk[0], chunk[1], freqs)
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo

def mergeExtraPunctuation(seqa, seqb):
    if len(seqa) == 0 or len(seqb) == 0:
        if len(seqb) == 0:
            seqa,seqb = seqb,seqa
        if not re.search(r'\w', ''.join([s.val for s in seqb])):
            return mergeChunk(seqa, seqb)
    return [seqa, seqb]
    
def doExtraPunctuationMerge(mergeInfo):
    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            chunk = mergeExtraPunctuation(chunk[0], chunk[1])
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo

def nonAlphaNumCount(s):
    return sum(int(not c.isalnum()) for c in s)
    
def mergePunctuationGarbage(seqa, seqb):
    aPunctCount = nonAlphaNumCount(''.join([s.val for s in seqa]))
    bPunctCount = nonAlphaNumCount(''.join([s.val for s in seqb]))
    aNonPunctCount = len(''.join([s.val for s in seqa])) - aPunctCount
    bNonPunctCount = len(''.join([s.val for s in seqb])) - bPunctCount
    if aNonPunctCount < 2*bNonPunctCount and bNonPunctCount < 2*aNonPunctCount:
        if aPunctCount < bPunctCount:
            return mergeChunk(seqa, seqb)
        if aPunctCount > bPunctCount:
            return mergeChunk(seqb, seqa)
    return [seqa, seqb]
    
def doPunctuationGarbageMerge(mergeInfo):
    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            chunk = mergePunctuationGarbage(chunk[0], chunk[1])
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo
    
def doGuessMerge(mergeInfo):
    revisedMergeInfo = []
    for chunk in mergeInfo:
        if len(chunk) == 2:
            chunk = mergeChunk(chunk[0], chunk[1], False)
        if len(revisedMergeInfo) and len(chunk) == len(revisedMergeInfo[-1]) == 1:
            revisedMergeInfo[-1][0].extend(chunk[0])
        else:
            revisedMergeInfo.append(chunk)
    return revisedMergeInfo
    
def getMergeInfo(atoks_full, btoks_full):
    atoks = [t.val+t.after for t in atoks_full]
    btoks = [t.val+t.after for t in btoks_full]
    alines = []
    blines = []
    bothlines = []
    mergeInfo = []
    i = j = 0
    for diffinfo in [s.strip().split(' ', 1) for s in difflib.ndiff(atoks, btoks) if not s.startswith('?')]:
        if len(diffinfo) == 1:
            if len(alines) + len(blines):
                mergeInfo.append([alines, blines])
                alines = []
                blines = []
            bothlines.append(atoks_full[i])
            i += 1
            j += 1
        elif diffinfo[0] == '-':
            if len(bothlines):
                mergeInfo.append([bothlines])
                bothlines = []
            alines.append(atoks_full[i])
            i += 1
        elif diffinfo[0] == '+':
            if len(bothlines):
                mergeInfo.append([bothlines])
                bothlines = []
            blines.append(btoks_full[j])
            j += 1
    if len(alines) + len(blines):
        mergeInfo.append([alines, blines])
    if len(bothlines):
        mergeInfo.append([bothlines])
    return mergeInfo


def getLineTokens(text, toks):
    tokI = 0
    for line in text.split('\n'):
        linetoks = line.split()
        linetokI = 0
        revisedlinetoks = []
        hasSpace = []
        while linetokI < len(linetoks) and tokI < len(toks):
            if len(linetoks[linetokI]) == len(toks[tokI]):
                revisedlinetoks.append(toks[tokI])
                hasSpace.append(True)
                tokI += 1
                linetokI += 1
            elif len(linetoks[linetokI]) < len(toks[tokI]):
                revisedlinetoks.append(toks[tokI])
                hasSpace.append(True)
                mylen = len(linetoks[linetokI])
                while linetokI < len(linetoks)-1 and mylen < len(toks[tokI]):
                    linetokI += 1
                    mylen += len(linetoks[linetokI])
                linetokI += 1
                tokI += 1
            else:
                revisedlinetoks.append(toks[tokI])
                mylen = len(toks[tokI])
                hasSpace.append(True)
                while tokI < len(toks)-1 and mylen < len(linetoks[linetokI]):
                    tokI += 1
                    mylen += len(toks[tokI])
                    revisedlinetoks.append(toks[tokI])
                    hasSpace.append(False)
                tokI += 1
                linetokI += 1
            if len(hasSpace):
                hasSpace[0] = False
        yield revisedlinetoks, [int(space) * ' ' for space in hasSpace[1:]] + ['\n']

def printPreserveSpacing(toks, fileHandle, colored=False):
    toPrint = []
    newline = '<br/>' if html else '\n'
    for tok in toks:
        if colored:
            toPrint.append(tok.repr.replace('\n', newline))
        else:
            toPrint.append(tok.val + tok.after.replace('\n', newline))
    if html:
        toPrint = ['<span>'] + toPrint + ['</span>']
    print(''.join(toPrint), file=fileHandle)

def getCommonToks(afiles, bfiles):
    c = Counter()
    for afile, bfile in zip(afiles, bfiles):
        atoks = tokenize(afile)
        btoks = tokenize(bfile)
        mergeInfo = getMergeInfo(atoks, btoks)
        for m in mergeInfo:
            if len(m) == 1:
                for tok in m[0]:
                    if not re.search('[0-9]', tok.val):
                        c[tok.val] += 1
    return c

afiles = sorted(os.path.join(sys.argv[1], f) for f in os.listdir(sys.argv[1]))
bfiles = sorted(os.path.join(sys.argv[2], f) for f in os.listdir(sys.argv[2]))
outfolder = sys.argv[3]
debug = (len(sys.argv) > 4) and ('d' in sys.argv[4])
html = (len(sys.argv) > 4) and ('h' in sys.argv[4])
colored = (len(sys.argv) > 4) and ('c' in sys.argv[4])

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

internalUnigrams = getCommonToks(afiles, bfiles)
for afile, bfile in zip(afiles, bfiles):
    atoks = tokenize(afile)
    btoks = tokenize(bfile)

    mergeInfo = getMergeInfo(atoks, btoks)
    mergeInfo = doSpellingMerge(mergeInfo)
    mergeInfo = doCapitalizationMerge(mergeInfo)
    mergeInfo = doUnigramFrequncyMerge(mergeInfo, internalUnigrams)
    mergeInfo = doExtraPunctuationMerge(mergeInfo)
    mergeInfo = doPunctuationGarbageMerge(mergeInfo)
    mergeInfo = doGuessMerge(mergeInfo)
    if len(mergeInfo):
        toks = mergeInfo[0][0]
    else:
        toks = []

    markNonWords(toks)
    
    with open(os.path.join(outfolder, os.path.basename(afile)), 'w') as fileHandle:
        printPreserveSpacing(toks, fileHandle, debug or colored)
