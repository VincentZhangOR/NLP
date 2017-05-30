#!/usr/bin/env python
from __future__ import division
import sys
from collections import defaultdict
import math

def calculate(epronInputs, jpronInputs):

    forward = defaultdict(lambda: defaultdict(float))
    backward = defaultdict(lambda: defaultdict(float))
    fraccount = defaultdict(lambda: defaultdict(float))

    # initial table
    eset = set()
    for eprons in epronInputs:
        for epron in eprons:
            eset.add(epron)

    jset = set()
    for jprons in jpronInputs:
        for start in xrange(len(jprons)):
            for k in xrange(1,4):
                jpron = ' '.join(jprons[start:min(start+k, len(jprons))])
                jset.add(jpron)

    totalpair = len(eset) * len(jset)
    for e in eset:
        for j in jset:
            table[e][j] = 1/totalpair

    for iter in xrange(max_iter):
        totalprob = 0.0
        fraccount.clear()
        for index in xrange(len(epronInputs)):
            eprons = epronInputs[index]
            jprons = jpronInputs[index]
            n, m = len(eprons), len(jprons)

            # forward phase
            forward.clear()
            forward[0][0] = 1.0
            for i in xrange(0, n):
                epron = eprons[i]
                for j in forward[i]:
                    for k in xrange(1, min(m-j, 3)+1):
                        jpron = ' '.join(jprons[j:j+k])
                        score = forward[i][j] * table[epron][jpron]
                        forward[i+1][j+k] += score

            # backward phase
            backward.clear()
            backward[n][m] = 1.0
            for i in xrange(n, 0, -1):
                epron = eprons[i-1]
                for j in backward[i]:
                    for k in xrange(1, min(j, 3)+1):
                        jpron = ' '.join(jprons[j-k:j])
                        score = backward[i][j] * table[epron][jpron]
                        backward[i-1][j-k] += score

            # fraction count
            for i in xrange(0, n):
                epron = eprons[i]
                for j in forward[i]:
                    for k in xrange(1, min(m-j, 3)+1):
                        jpron = ' '.join(jprons[j:j+k])
                        score = forward[i][j] * backward[i+1][j+k] * table[epron][jpron] / forward[n][m]
                        fraccount[epron][jpron] += score

            totalprob += math.log(forward[n][m],2)

        table.clear()
        for epron in fraccount:
            total = sum(fraccount[epron].values())
            for jpron in fraccount[epron]:
                table[epron][jpron] = fraccount[epron][jpron] / total

        # print
        nonzeros = 0
        sys.stderr.write('iteration ' + str(iter) + ' ----- ' + 'corpus prob= 2^' + str(totalprob) + '\n')
        for e in table:
            if len(e) == 1:
                sys.stderr.write(e + '|->  ', )
            else:
                sys.stderr.write(e + '|-> ', )
            sort_d = sorted(zip(table[e].values(), table[e].keys()), reverse=True)
            for n, (p, j) in enumerate(sort_d):
                if p >= 0.01:
                    nonzeros += 1
                    if n + 1 < len(sort_d) and sort_d[n + 1][0] >= 0.01:
                        sys.stderr.write(j + ': ' + str('%3.2f' % p) + ' ')
                    else:
                        sys.stderr.write(j + ': ' + str('%3.2f' % p) + '\n')
        sys.stderr.write('nonzeros = ' + str(nonzeros) + '\n\n')

# main
inputs = sys.stdin.readlines()
max_iter = int(sys.argv[1])

table = defaultdict((lambda: defaultdict(float)))
epronInputs = []
jpronInputs = []
for i in xrange(0,len(inputs),3):
    epronInputs.append(inputs[i].split())
    jpronInputs.append(inputs[i+1].split())

calculate(epronInputs,jpronInputs)

for e in table:
    all = sum([x for x in table[e].values() if x >= 0.01])
    # all = sum([x for x in allcnt[e].values()])
    for j in table[e]:
        if all > 0.0:
            p = table[e][j] / all
            if p >= 0.01:
                sys.stdout.write(e + ' : ' + j + ' # ' + str(p) + '\n')