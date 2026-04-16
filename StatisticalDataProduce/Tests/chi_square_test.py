#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import chi_square_test

RESULT_FILE = "Results/chi_square_test.txt"


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    chi_value = chi_square_test(data)
    output = (
        "CHI-SQUARE TEST RESULTS\n"
        "========================\n"
        f"Chi-Square Value: {chi_value:.6f}\n"
        "Expected range for random data: ~200-300\n"
    )

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        out.write(output)

    print(f"Chi-square test saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
