#!/bin/bash

# Change the algorithm name to the desired algorithm
ALG=AES_256

echo "from $ALG import *" > Alg.py

echo Algorithm: $ALG


# Correlation Tests

echo "Running Correlation Tests"
python3 corr_rk_rk.py &
python3 corr_rc_rc.py &
python3 corr_mk_rk.py &
python3 corr_p_rc.py &
python3 corr_mk_rc.py &


# Avalance Tests

echo "Running Avalanche Tests"
python3 aval_mk_rc.py & 
python3 aval_mk_rk.py & 
python3 aval_p_rc.py &

# Move the drawings to the Results folder
mv -t Results/ aval_mk-rc.png aval_mk-rk.png aval_p-rc.png corr_mk-rk.png corr_p-rc.png corr_mk-rc.png corr_rk-rk.png corr_rc-rc.png