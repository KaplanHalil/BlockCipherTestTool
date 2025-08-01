#!/bin/bash

# Before running change the environment to PyPy with "source myenv/bin/activate"

# Change the algorithm name to the desired algorithm
ALG=PRESENT80

echo "from $ALG import *" > Algorithm/Alg.py

echo "### Test is starting ###"

echo Algorithm: $ALG

# Remove the previous results
rm -f Results/*a

# Avalance Tests

echo "Running Avalanche Tests"
pypy3 AvalCorrTests/aval_mk_rc.py & 
pypy3 AvalCorrTests/aval_mk_rk.py & 
pypy3 AvalCorrTests/aval_p_rc.py &

# Correlation Tests

echo "Running Correlation Tests"
pypy3 AvalCorrTests/corr_rk_rk.py &
pypy3 AvalCorrTests/corr_mk_rk.py &
pypy3 AvalCorrTests/corr_p_rc.py &
pypy3 AvalCorrTests/corr_mk_rc.py &
pypy3 AvalCorrTests/corr_rc_rc.py &

# S-box Tests

echo "Running S-box Tests"
sage SboxTest/sboxTest.sage > Results/sbox_tests.txt &

# Data for Statistical Tests

echo "Producing cipher-texts for statistical tests"
pypy3 StatisticalDataProduce/cbc_write_to_folder.py 

# Move the drawings to the Results folder
mv -t Results/ aval_mk-rc.png aval_mk-rk.png aval_p-rc.png corr_mk-rk.png corr_p-rc.png corr_mk-rc.png corr_rk-rk.png corr_rc-rc.png

# Move the produced cipher-texts to the Results folder
mv ciphertext.hex Results/

# Move the produced DDT and BCT drawings to the Results folder
mv -t Results/ BCT.png DDT.png 

echo "### Test is done ###"
