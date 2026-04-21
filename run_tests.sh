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
python3 AvalCorrTests/aval_mk_rc.py  --workers 16
python3 AvalCorrTests/aval_mk_rk.py  --workers 16
python3 AvalCorrTests/aval_p_rc.py --workers 16

# Correlation Tests

echo "Running Correlation Tests"

python3 AvalCorrTests/corr_mk_rk.py --workers 16
python3 AvalCorrTests/corr_p_rc.py --workers 16
python3 AvalCorrTests/corr_mk_rc.py --workers 16
python3 AvalCorrTests/corr_rk_rk.py --workers 16 
python3 AvalCorrTests/corr_rc_rc.py --workers 16

echo "Running S-box Tests"
#sage SboxTest/sboxTest.sage > Results/sbox_tests.txt &


echo "Producing cipher-texts for statistical tests"
#python3 StatisticalDataProduce/DataGeneration/ctr_write_to_folder.py --size-mb 20 --workers 16 --skip-analysis --output Results/ciphertext.hex

echo "Running combined statistical tests"
#python3 StatisticalDataProduce/Tests/ciphertext_analysis.py --parallel

echo "Running interpolation attack analysis"
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 0 --sample-count 257 --parallel --workers 16 --output Results/interpolation_0.txt
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 1 --sample-count 1000 --parallel --workers 16 --output Results/interpolation_1.txt
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 2 --sample-count 1000 --parallel --workers 16 --output Results/interpolation_2.txt
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 14 --sample-count 1000 --parallel --workers 16 --output Results/interpolation_31.txt
#python3 InterpolationTests/interpolation_attack_test.py --variable-byte 15 --sample-count 1000 --parallel --workers 16 --output Results/interpolation_30.txt
wait

echo "### Test is done ###"
