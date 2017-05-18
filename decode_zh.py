#!/usr/bin/env python
import sys
from collections import defaultdict

# read in trigram model data
f = open(sys.argv[1])
lines = f.readlines()
trigram = defaultdict(lambda: defaultdict(dict))
for line in lines:
    input = line.split()
    prev2, prev1 = input[0], input[1]
    cur = input[3]
    p = float(input[5])
    trigram[cur][prev1][prev2] = p
    if cur == '</s>':
        trigram[cur][cur][prev1] = 1.0
f.close()

# read in mapping between english phonemes and katakana phonemes
f = open(sys.argv[2])
lines = f.readlines()
epron_jpron = defaultdict(lambda: defaultdict(float))
for line in lines:
    input = line.split()
    p = float(input[-1])
    epron = input[0]
    jpron = ''
    if len(input) == 5:
        jpron = (input[2],)
    elif len(input) == 6:
        jpron = (input[2], input[3])
    else:
        jpron = (input[2], input[3], input[4])
    epron_jpron[jpron][epron] = p
epron_jpron[('</s>',)]['</s>'] = 1.0
f.close()

best = defaultdict(lambda: defaultdict(float))
back = defaultdict(lambda: defaultdict(tuple))

# using viterbi algorithm to calculate best possible path of generating katakana phoneme from english phoneme given tri-gram model
def viterbi(inputs):
    defaultdict.clear(back)
    defaultdict.clear(best)
    best[0]['<s>', '<s>'] = 1.0
    best[1]['<s>', '<s>'] = 1.0
    for i in xrange(2, len(inputs)):   # 0,1 are both <s>
        for k in xrange(1,4):   # one english phonemes can map to 1 or 2 or 3 katakana phonemes
            jpron = tuple(inputs[i-k+1:i+1])
            if jpron in epron_jpron:
                for epron in epron_jpron[jpron]:
                    for epre1, epre2 in best[i-k]:
                        temp = best[i-k][epre1, epre2] * trigram[epron][epre1][epre2] * epron_jpron[jpron][epron]  # HMM fomula
                        if temp > best[i][epron, epre1]:
                            best[i][epron, epre1] = temp
                            back[i][epron, epre1] = (k, epre2)

def backtrack(i, epron, epre1):
    if i < 2:
        return ''
    k, epre2 = back[i][epron, epre1]
    return backtrack(i-k, epre1, epre2) + epron + ' '


katakanaList = sys.stdin.readlines()  # read in katakana sequences
for s in katakanaList:
    katakana = ('<s> <s> ' + s + ' </s> </s>').split()
    viterbi(katakana)
    ans = backtrack(len(katakana)-1, '</s>', '</s>')[:-10]
    print 'Katakana:', s
    print 'English:', ans + '# ' + str('%.6e' % best[len(katakana)-1]['</s>', '</s>'])
    print '\n'