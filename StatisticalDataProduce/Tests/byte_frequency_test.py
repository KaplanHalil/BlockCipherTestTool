#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import byte_frequency_analysis

RESULT_FILE = "Results/byte_frequency_test.txt"


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    bf = byte_frequency_analysis(data)
    output = (
        "BYTE FREQUENCY TEST RESULTS\n"
        "===========================\n"
        f"Average Frequency: {bf['avg_frequency']:.8f}\n"
        f"Standard Deviation: {bf['std_dev']:.8f}\n"
        f"Min Frequency: {bf['min_freq']:.8f}\n"
        f"Max Frequency: {bf['max_freq']:.8f}\n"
    )

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        out.write(output)

    print(f"Byte frequency test saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
