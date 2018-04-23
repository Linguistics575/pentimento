#!/usr/bin/python3

import sys
import difflib
import nltk
import re
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


p = PorterStemmer()
wikiwords = set([line.split('\t')[0] for line in open('../WikipediaTitles/titleWordCount.tsv')])
words = set([line.strip() for line in open('../spellchecker/words.txt').readlines()])
lemmas = set([p.stem(word, 0, len(word)-1) for word in words])

def isMorphologicallyPlausable(word, dictionary, allowLemma=False):
    parts = re.split("['.-]", word)
    for elem in parts:
        if re.search(r'[a-zA-Z]', elem) and elem.lower() not in dictionary:
            if not (allowLemma and p.stem(elem.lower(), 0, len(elem)-1) in lemmas):
                return False
    return True

def areWords(seq, dictionary, allowLemma=False):
    for elem in seq:
        if re.search(r'[a-zA-Z]', elem) and not isMorphologicallyPlausable(elem, dictionary, allowLemma):
            return False
    return True

def mergeAlternateSpelling(seqa, seqb):
    for allowLemma in [False, True]:
        for dic in [words, wikiwords]:
            areWordsA = areWords(seqa, dic, allowLemma)
            areWordsB = areWords(seqb, dic, allowLemma)
            if areWordsA and not areWordsB:
                return [seqa]
            if not areWordsA and areWordsB:
                return [seqb]
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
        if prev == '.':
            if not cur[0].isupper():
                return False
        else:
            if cur not in words:
                return False
    return True

def mergeAlternateCapitalization(seqa, seqb, prevToken):
    if ' '.join(seqa).lower() == ' '.join(seqb).lower():
        aIsCorrect = isCorrectCapitalization(seqa, prevToken)
        bIsCorrect = isCorrectCapitalization(seqb, prevToken)
        if aIsCorrect and not bIsCorrect:
            return [seqa]
        if not aIsCorrect and bIsCorrect:
            return [seqb]
        if aIsCorrect and bIsCorrect:
            if ' '.join(seqa).islower():
                return [seqa]
            if ' '.join(seqb).islower():
                return [seqb]
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
            aScore *= (wordFreq.get(word) or 0)
        for word in seqb:
            bScore *= (wordFreq.get(word) or 0)
        if aScore > bScore:
            return [seqa]
        if bScore > aScore:
            return [seqb]
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
        if not re.search(r'\w', ''.join(seqb)):
            return [seqa]
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
    aPunctCount = nonAlphaNumCount(''.join(seqa))
    bPunctCount = nonAlphaNumCount(''.join(seqb))
    if aPunctCount < bPunctCount:
        return [seqa]
    if aPunctCount > bPunctCount:
        return [seqb]
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
    
def getMergeInfo(atoks, btoks):
    alines = []
    blines = []
    bothlines = []
    mergeInfo = []
    for diffinfo in [s.strip().split(' ', 1) for s in difflib.ndiff(atoks, btoks) if not s.startswith('?')]:
        if len(diffinfo) == 1:
            if len(alines) + len(blines):
                mergeInfo.append([alines, blines])
                alines = []
                blines = []
            bothlines.append(diffinfo[-1])
        elif diffinfo[0] == '-':
            if len(bothlines):
                mergeInfo.append([bothlines])
                bothlines = []
            alines.append(diffinfo[-1])
        elif diffinfo[0] == '+':
            if len(bothlines):
                mergeInfo.append([bothlines])
                bothlines = []
            blines.append(diffinfo[-1])
    if len(alines) + len(blines):
        mergeInfo.append([alines, blines])
    if len(bothlines):
        mergeInfo.append([bothlines])

    return mergeInfo

def tokenize(filename):
    text = ''.join(open(filename).readlines()).replace('-\n', '')
    return nltk.word_tokenize(text)

def getLineTokens(text, toks):
    tokI = 0
    for line in text.split('\n'):
        print(line)
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
        yield revisedlinetoks, hasSpace

def printPreserveSpacing(basefilename, mergedToks):
    text = ''.join(open(basefilename).readlines()).replace('-\n', '')
    toks = nltk.word_tokenize(text)
    mergeInfo = getMergeInfo(toks, mergedToks)
    chunkNumber = 0
    i = j = 0
    for line, hasSpaces in getLineTokens(text, toks):
        lineToPrint = ''
        for tok,hasSpace in zip(line, hasSpaces):
            if len(mergeInfo[chunkNumber][0]) == i:
                chunkNumber += 1
                i = j = 0
            if len(mergeInfo[chunkNumber]) == 2 and j == 0:
                if lineToPrint:
                    lineToPrint += ' '
                lineToPrint +=  ' '.join(mergeInfo[chunkNumber][1])
                j = 1
            if len(mergeInfo[chunkNumber]) == 1:
                if hasSpace:
                    lineToPrint += ' '
                lineToPrint += mergeInfo[chunkNumber][0][i]
            i += 1
        print(lineToPrint)

atoks = tokenize(sys.argv[1])
btoks = tokenize(sys.argv[2])

mergeInfo = getMergeInfo(atoks, btoks)
mergeInfo = doSpellingMerge(mergeInfo)
mergeInfo = doCapitalizationMerge(mergeInfo)
mergeInfo = doUnigramFrequncyMerge(mergeInfo)
mergeInfo = doExtraPunctuationMerge(mergeInfo)
mergeInfo = doPunctuationGarbageMerge(mergeInfo)
mergeInfo = doGuessMerge(mergeInfo)

for i in mergeInfo:
    if len(i) == 2:
        print(i)

printPreserveSpacing(sys.argv[1], mergeInfo[0][0])
