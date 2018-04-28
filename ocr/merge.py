#!/usr/bin/python3

import sys
import difflib
import nltk
import re
import os
from PorterStemmer import PorterStemmer

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    #todo: print in colors, to display when we have errors
    #print(bcolors.WARNING + "Warning: No active frommets remain. Continue?" + bcolors.ENDC)

def blue(text):
    return bcolors.OKBLUE + text + bcolors.ENDC

def yellow(text):
    return bcolors.WARNING + text + bcolors.ENDC

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
        for tok,after in zip(line, afters):
            tokens.append(Token(tok, after, filename))
    return tokens

p = PorterStemmer()
wikiwords = set([line.split('\t')[0] for line in open('../WikipediaTitles/titleWordCount.tsv')])
words = set([line.strip() for line in open('../spellchecker/words.txt').readlines()])
lemmas = set([p.stem(word, 0, len(word)-1) for word in words])

def mergeChunk(keep, reject=None):
    for tok in keep:
        tok.repr = blue(tok.repr)
    for tok in reject:
        tok.repr = yellow(strike(tok.repr))
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
            aScore *= (wordFreq.get(word.val) or 0)
        for word in seqb:
            bScore *= (wordFreq.get(word.val) or 0)
        if aScore > bScore:
            return mergeChunk(seqa, seqb)
        if bScore > aScore:
            return mergeChunk(seqb, seqa)
    return [seqa, seqb]

def doUnigramFrequncyMerge(mergeInfo):
    freqs = {s.split('\t')[0]: int(s.split('\t')[1]) for s in open('brown_freq.txt').readlines()}

    revisedMergeInfo = []
    for chunk in mergeInfo:
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
            chunk = [chunk[0]]
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

def printPreserveSpacing(toks, fileHandle, debug=False):
    toPrint = []
    for tok in toks:
        if debug:
            toPrint.append(tok.repr)
        else:
            toPrint.append(tok.val + tok.after)
    print(''.join(toPrint), file=fileHandle)

afiles = sorted(os.path.join(sys.argv[1], f) for f in os.listdir(sys.argv[1]))
bfiles = sorted(os.path.join(sys.argv[2], f) for f in os.listdir(sys.argv[2]))
outfolder = sys.argv[3]
debug = (len(sys.argv) > 4) and ('d' in sys.argv[4])

if not os.path.exists(outfolder):
    os.makedirs(outfolder)

for afile, bfile in zip(afiles, bfiles):
    atoks = tokenize(afile)
    btoks = tokenize(bfile)

    mergeInfo = getMergeInfo(atoks, btoks)
    mergeInfo = doSpellingMerge(mergeInfo)
    mergeInfo = doCapitalizationMerge(mergeInfo)
    mergeInfo = doUnigramFrequncyMerge(mergeInfo)
    mergeInfo = doExtraPunctuationMerge(mergeInfo)
    mergeInfo = doPunctuationGarbageMerge(mergeInfo)
    mergeInfo = doGuessMerge(mergeInfo)
    
    with open(os.path.join(outfolder, os.path.basename(afile)), 'w') as fileHandle:
        if len(mergeInfo):
            printPreserveSpacing(mergeInfo[0][0], fileHandle, debug)
