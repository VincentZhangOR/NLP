#!/usr/bin/env python
from __future__ import division
import sys
from collections import defaultdict
import math

def calculate(epronInputs, jpronInputs):

    def mapping(epron, jpron, l):# enumerate all legal alignments for the E-J pair
        if len(jpron) == 0:
            return
        if len(epron) == 1:
            if len(jpron) > 3:
                return
            jpron_str = ' '.join(jpron)
            l.append((epron[0],jpron_str))
            s.append(l)
            return
        for i in xrange(1,4):
            newl = []
            jpron_str = ' '.join(jpron[:i])
            newl.append((epron[0],jpron_str))
            mapping(epron[1:], jpron[i:], l+newl)

    temp_list = [[] for x in xrange(len(epronInputs))]
    cprob = 0.0
    for index in xrange(len(epronInputs)):
        epronInput = epronInputs[index]
        jpronInput = jpronInputs[index]
        s = []
        mapping(epronInput, jpronInput, [])
        allmapping.append(s)
        temp_list[index] = [1 / len(s) for x in xrange(len(s))]
        temp_cprob = (1 / (len(s[0]) * len(s))) ** len(s[0]) * len(s)
        cprob += math.log(temp_cprob,2)

    for iter in xrange(max_iter):
        if iter > 0:
            cprob = 0.0

        for index in xrange(len(epronInputs)):
            ss = allmapping[index]

            if iter > 0:
                # calculate corpus probability
                for e in d[index]:
                    for j in d[index][e]:
                        for zi in d[index][e][j]:
                            d[index][e][j][zi] = allcnt[e][j]

                temp_cprob = 0.0
                for zi, x in enumerate(ss):
                    p = 1.0
                    for e, j in x:
                        p *= d[index][e][j][zi]
                    temp_cprob += p
                cprob += math.log(temp_cprob,2)

                # calculate each alignments respective probability
                temp_list[index] = []
                for zi, x in enumerate(ss):
                    temp_p = 1.0
                    for e, j in x:
                        temp_p *= d[index][e][j][zi]
                    temp_list[index].append(temp_p)

                temp_list[index] = map(lambda x: x / sum(temp_list[index]), temp_list[index]) # renormalize the probabilities to get a distribution over these alignments

            d[index].clear()
            for zi,x in enumerate(ss):
                for e,j in x:
                    d[index][e][j][zi] = temp_list[index][zi] # / sum(cnt[e,j].values())

        allcnt.clear()
        for index in xrange(len(epronInputs)):
            for e in d[index]:
                for j in d[index][e]:
                    allcnt[e][j] += sum(d[index][e][j].values())

        for e in allcnt:
            total = sum(allcnt[e].values())
            for j in allcnt[e]:
                allcnt[e][j] /= total

        # print
        nonzeros = 0
        sys.stderr.write('iteration ' + str(iter) + ' ----- ' + 'corpus prob= 2^' + str(cprob) + '\n')
        for e in allcnt:
            if len(e) == 1:
                sys.stderr.write(e + '|->  ', )
            else:
                sys.stderr.write(e + '|-> ', )
            sort_d = sorted(zip(allcnt[e].values(),allcnt[e].keys()),reverse = True)
            for n, (p, j) in enumerate(sort_d):
                if p >= 0.01:
                    nonzeros += 1
                    if n+1 < len(sort_d) and sort_d[n+1][0] >= 0.01:
                        sys.stderr.write(j + ': ' + str('%3.2f' % p) + ' ')
                    else:
                        sys.stderr.write(j + ': ' + str('%3.2f' % p) + '\n')
        sys.stderr.write('nonzeros = ' + str(nonzeros) + '\n\n')

# main
inputs = sys.stdin.readlines()
max_iter = int(sys.argv[1])

allmapping = []
d = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda: defaultdict(float))))
allcnt = defaultdict(lambda: defaultdict(float))
s = []

len_inputs = len(inputs)
epronInputs = []
jpronInputs = []
for i in xrange(0,len_inputs,3):
    epronInputs.append(inputs[i].split())
    jpronInputs.append(inputs[i+1].split())

calculate(epronInputs,jpronInputs)

for e in allcnt:
    all = sum([x for x in allcnt[e].values() if x >= 0.01])
    # all = sum([x for x in allcnt[e].values()])
    for j in allcnt[e]:
        if all > 0.0:
            p = allcnt[e][j] / all
            if p >= 0.01:
                sys.stdout.write(e + ' : ' + j + ' # ' + str(p) + '\n')