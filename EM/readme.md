This folder contains code and data for learning between Katakana pronounciation and English pronounciation using EM algorithm.

em.py uses non-dp version.

em2.py uses dp version (forword-backword algorithm).

the command:
cat epron-jpron.data | ./em.py 15 >epron-jpron.probs 2>epron-jpron.logs              # training
