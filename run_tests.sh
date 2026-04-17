#!/bin/bash

# Change the algorithm name to the desired algorithm
ALG=AES_256

echo "from $ALG import *" > Algorithm/Alg.py

echo "### Test is starting ###"

echo Algorithm: $ALG

# Remove the previous results
rm -f Results/*

# Avalance Tests

echo "Running Avalanche Tests"
#python3 AvalCorrTests/aval_mk_rc.py & 
#python3 AvalCorrTests/aval_mk_rk.py & 
#python3 AvalCorrTests/aval_p_rc.py &

# Correlation Tests

echo "Running Correlation Tests"
#python3 AvalCorrTests/corr_rk_rk.py &
#python3 AvalCorrTests/corr_mk_rk.py &
#python3 AvalCorrTests/corr_p_rc.py &
#python3 AvalCorrTests/corr_mk_rc.py &
#python3 AvalCorrTests/corr_rc_rc.py &

echo "Running S-box Tests"
#sage SboxTest/sboxTest.sage > Results/sbox_tests.txt &


echo "Producing cipher-texts for statistical tests"
python3 StatisticalDataProduce/DataGeneration/ctr_write_to_folder.py --size-mb 20 --workers 16 --skip-analysis --output Results/ciphertext.hex

echo "Running combined statistical tests"
python3 StatisticalDataProduce/Tests/ciphertext_analysis.py --parallel

echo "Running interpolation attack analysis"
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 3 --sample-count 257 --parallel --workers 16 --output Results/interpolation_attack_test.txt

wait

echo "### Test is done ###"
