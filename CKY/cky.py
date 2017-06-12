#!/usr/bin/env python

import sys
from collections import defaultdict
from tree import Tree

def unary(i,j,sentence):
    for r1 in runa:
        for r2 in runa[r1]:
            score = runa[r1][r2] * d[i][j][r2[0]]
            if score > d[i][j][r1]:
                if r2[0] in sentence:
                    if r2[0] == sentence[i]:
                        d[i][j][r1] = score
                        back[i][j][r1] = ('Terminal', r2)
                else:
                    d[i][j][r1] = score
                    back[i][j][r1] = ('NonTerminal', r2)

def cky(sentence):
    d.clear()
    back.clear()
    n = len(sentence)

    for ii in xrange(n):
        for r1 in runa:
            for r2 in runa[r1]:
                if r2[0] in sentence:
                    if r2[0] == sentence[ii]:
                        d[ii][ii+1][r2[0]] = 1.0

    for diff in xrange(1,n+1):
        for i in xrange(n - diff + 1):
            j = i + diff
            for k in xrange(i+1, j):
                for r1 in rbin:
                    for r2 in rbin[r1]:
                        score = rbin[r1][r2] * d[i][k][r2[0]] * d[k][j][r2[1]]
                        if score > d[i][j][r1]:
                            d[i][j][r1] = score
                            back[i][j][r1] = (k, r2)
            for mm in xrange(10):
                unary(i,j,sentence)
    for i in xrange(10):
        unary(0, len(sentence), sentence)

def backtrack(i,j,r1,sentence_origin):
    if back[i][j][r1] == None:
        return ''
    (k, r2) = back[i][j][r1]
    if k == 'Terminal':
        return '(' + r1 + ' ' + sentence_origin[i] + ')'
    elif k == 'NonTerminal':
        return '(' + r1 + ' ' + backtrack(i,j,r2[0],sentence_origin) + ')'
    else:
        return '(' + r1 + ' ' + backtrack(i,k,r2[0],sentence_origin) + ' ' + backtrack(k,j,r2[1],sentence_origin) + ')'

def debinarize(t):
    if t.is_terminal():
        return t.dostr()
    res = ''
    if t.label[-1] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        res += '(' + t.label + ' '
        for i,x in enumerate(t.subs):
            if i < len(t.subs) - 1:
                res += debinarize(x) + ' '
            else:
                res += debinarize(x)
        res += ')'
    else:
        for i,x in enumerate(t.subs):
            if i < len(t.subs) - 1:
                res += debinarize(x) + ' '
            else:
                res += debinarize(x)
    return res

# main
d = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
back = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
rbin = defaultdict(lambda: defaultdict(float))
runa = defaultdict(lambda: defaultdict(float))
lexicon = set()

if len(sys.argv) > 2:
    file2 = sys.argv[2]
    f = open(file2)
    words = f.readlines()
    for word in words:
        lexicon.add(word.split()[0])

# read in grammers
file1 = sys.argv[1]
f = open(file1)
rules = f.readlines()
for rule in rules[1:]:
    p = rule.split()
    k1 = p[0]
    if len(p) == 5:
        k2 = (p[2],)
        runa[k1][k2] = float(p[-1])
    else:
        k2 = (p[2],p[3])
        rbin[k1][k2] = float(p[-1])

lines = sys.stdin.readlines()
for line in lines:
    sentence_origin = line.split()
    sentence = []
    for x in sentence_origin:
        if len(sys.argv) > 2 and x not in lexicon:
            x = '<unk>'
        sentence.append(x)
    cky(sentence)
    res = backtrack(0,len(sentence),'TOP',sentence_origin)
    if len(res) != 0:
        print debinarize(Tree.parse(res))
    else:
        print 'NONE'