#!/bin/bash

# Before running change the environment to PyPy with "source myenv/bin/activate"

# Change the algorithm name to the desired algorithm
ALG=AES_256

echo "from $ALG import *" > Algorithm/Alg.py

echo Algorithm: $ALG

# Remove the previous results
rm -f Results/*

# Avalance Tests

echo "Running Avalanche Tests"
#pypy3 AvalCorrTests/aval_mk_rc.py & 
pypy3 AvalCorrTests/aval_mk_rk.py & 
#pypy3 AvalCorrTests/aval_p_rc.py &

# Correlation Tests

echo "Running Correlation Tests"
#pypy3 AvalCorrTests/corr_rk_rk.py &
#pypy3 AvalCorrTests/corr_mk_rk.py &
#pypy3 AvalCorrTests/corr_p_rc.py &
#pypy3 AvalCorrTests/corr_mk_rc.py &
#pypy3 AvalCorrTests/corr_rc_rc.py 

# Move the drawings to the Results folder
#mv -t Results/ AvalCorrTests/aval_mk-rc.png AvalCorrTests/aval_mk-rk.png AvalCorrTests/aval_p-rc.png AvalCorrTests/corr_mk-rk.png AvalCorrTests/corr_p-rc.png AvalCorrTests/corr_mk-rc.png AvalCorrTests/corr_rk-rk.png AvalCorrTests/corr_rc-rc.png

echo "Running S-box Tests"
sage SboxTest/sboxTest.sage > Results/sbox_tests.txt