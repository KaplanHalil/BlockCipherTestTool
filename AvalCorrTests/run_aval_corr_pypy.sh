#!/bin/bash

# Before running change the environment to PyPy with "source myenv/bin/activate"

# Change the algorithm name to the desired algorithm
ALG=AES_256

echo "from $ALG import *" > Alg.py

echo Algorithm: $ALG

# Remove the previous results
rm -f Results/*

# Avalance Tests

echo "Running Avalanche Tests"
pypy3 aval_mk_rc.py & 
pypy3 aval_mk_rk.py & 
pypy3 aval_p_rc.py &

# Correlation Tests

echo "Running Correlation Tests"
pypy3 corr_rk_rk.py &
pypy3 corr_mk_rk.py &
pypy3 corr_p_rc.py &
pypy3 corr_mk_rc.py &
pypy3 corr_rc_rc.py 

# Move the drawings to the Results folder
mv -t Results/ aval_mk-rc.png aval_mk-rk.png aval_p-rc.png corr_mk-rk.png corr_p-rc.png corr_mk-rc.png corr_rk-rk.png corr_rc-rc.png