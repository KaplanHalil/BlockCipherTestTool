#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import autocorrelation_analysis

RESULT_FILE = "Results/autocorrelation_test.txt"


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    ac = autocorrelation_analysis(data)
    output = (
        "AUTOCORRELATION TEST RESULTS\n"
        "===========================\n"
        f"Average Correlation: {ac['avg_correlation']:.6f}\n"
        f"Max Correlation: {ac['max_correlation']:.6f}\n"
        f"Number of Lags: {len(ac['lags'])}\n"
    )

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        out.write(output)

    print(f"Autocorrelation test saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
