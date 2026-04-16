#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import calculate_entropy, calculate_bit_entropy

RESULT_FILE = "Results/entropy_test.txt"


def format_results(byte_entropy, bit_entropy):
    return (
        "ENTROPY TEST RESULTS\n"
        "======================\n"
        f"Byte Entropy: {byte_entropy:.6f} bits\n"
        f"Bit Entropy:  {bit_entropy:.6f} bits\n"
        f"Byte entropy ideal: 8.000000\n"
        f"Bit entropy ideal: 1.000000\n"
    )


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    byte_entropy = calculate_entropy(data)
    bit_entropy = calculate_bit_entropy(data)
    output = format_results(byte_entropy, bit_entropy)

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        out.write(output)

    print(f"Entropy test saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
