#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import bit_frequency_analysis

RESULT_FILE = "Results/bit_frequency_test.txt"


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    bf = bit_frequency_analysis(data)
    output = (
        "BIT FREQUENCY TEST RESULTS\n"
        "==========================\n"
        f"Ones Ratio: {bf['ones_ratio']:.6f}\n"
        f"Zeros Ratio: {bf['zeros_ratio']:.6f}\n"
        f"Bit Bias: {bf['bias']:.6f}\n"
    )

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        out.write(output)

    print(f"Bit frequency test saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
