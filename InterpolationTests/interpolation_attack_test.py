#!/usr/bin/env python3
"""Interpolation resistance heuristic for block cipher output.

This test is not a formal attack, but it checks whether ciphertext bits
can be represented by a low-degree Boolean polynomial in a chosen
plaintext subspace. If many ciphertext bits admit low-degree ANF forms,
that suggests the cipher may be more vulnerable to algebraic or
interpolation-style analysis.
"""

import argparse
import math
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))

import Alg as cipher

RESULT_FILE = "Results/interpolation_attack_test.txt"


def bytes_to_bit_list(data):
    return [int(bit) for byte in data for bit in format(byte, '08b')]


def compute_anf_coeffs(truth):
    n = int(math.log2(len(truth)))
    if 1 << n != len(truth):
        raise ValueError("Truth table length must be a power of two")

    coeffs = truth.copy()
    size = len(coeffs)
    for bit in range(n):
        for mask in range(size):
            if mask & (1 << bit):
                coeffs[mask] ^= coeffs[mask ^ (1 << bit)]
    return coeffs


def anf_properties(truth):
    coeffs = compute_anf_coeffs(truth)
    nonzero = [mask for mask, value in enumerate(coeffs) if value]
    degree = max((mask.bit_count() for mask in nonzero), default=0)
    weight = len(nonzero)
    sparsity = weight / len(coeffs)
    return {
        'degree': degree,
        'weight': weight,
        'sparsity': sparsity,
    }


def encrypt_block(plaintext, key):
    rc = [[0] * cipher.ciphertext_size for _ in range(cipher.num_rounds)]
    ciphertext = cipher.encrypt(list(plaintext), key, rc)
    return bytes(ciphertext)


def parse_variable_bytes(spec):
    positions = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = part.split('-', 1)
            positions.update(range(int(start), int(end) + 1))
        else:
            positions.add(int(part))
    return sorted(positions)


def build_histogram(values):
    histogram = {}
    for value in values:
        histogram[value] = histogram.get(value, 0) + 1
    return {k: histogram[k] for k in sorted(histogram)}


def run_interpolation_test(variable_bytes, degree_threshold=3, sample_bits=8):
    if sample_bits < 1 or sample_bits > 8:
        raise ValueError("sample_bits must be between 1 and 8")

    for variable_byte in variable_bytes:
        if variable_byte < 0 or variable_byte >= cipher.plaintext_size:
            raise ValueError(f"variable_byte {variable_byte} is out of range")

    sample_size = 1 << sample_bits
    ciphertext_bits = cipher.ciphertext_size * 8
    key = [0] * cipher.mkey_size
    results_by_byte = {}

    for variable_byte in variable_bytes:
        plaintext = bytearray(cipher.plaintext_size)
        truth_tables = [[0] * sample_size for _ in range(ciphertext_bits)]

        for value in range(sample_size):
            plaintext[variable_byte] = value
            ciphertext = encrypt_block(plaintext, key)
            bit_list = bytes_to_bit_list(ciphertext)
            for bit_index in range(ciphertext_bits):
                truth_tables[bit_index][value] = bit_list[bit_index]

        properties = [anf_properties(table) for table in truth_tables]
        degrees = [p['degree'] for p in properties]
        weights = [p['weight'] for p in properties]
        low_degree_bits = [i for i, degree in enumerate(degrees) if degree <= degree_threshold]
        degree_histogram = build_histogram(degrees)
        weight_histogram = build_histogram(weights)

        results_by_byte[variable_byte] = {
            'ciphertext_bits': ciphertext_bits,
            'sample_bits': sample_bits,
            'degree_threshold': degree_threshold,
            'max_degree': max(degrees),
            'min_degree': min(degrees),
            'avg_degree': sum(degrees) / len(degrees),
            'low_degree_count': len(low_degree_bits),
            'low_degree_ratio': len(low_degree_bits) / len(degrees),
            'low_degree_bits': low_degree_bits[:20],
            'degrees': degrees,
            'degree_histogram': degree_histogram,
            'avg_weight': sum(weights) / len(weights),
            'min_weight': min(weights),
            'max_weight': max(weights),
            'weight_histogram': weight_histogram,
        }

    return {
        'variable_bytes': variable_bytes,
        'sample_bits': sample_bits,
        'degree_threshold': degree_threshold,
        'results_by_byte': results_by_byte,
    }


def format_histogram(histogram):
    return ', '.join(f"{k}:{v}" for k, v in histogram.items())


def format_results(results):
    lines = []
    lines.append("INTERPOLATION ATTACK RESISTANCE HEURISTIC")
    lines.append("========================================")
    lines.append(f"Variable plaintext byte positions: {results['variable_bytes']}")
    lines.append(f"Sample size per position: 2^{results['sample_bits']} = {1 << results['sample_bits']}")
    lines.append(f"Degree threshold: {results['degree_threshold']}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Each tested plaintext byte is varied over the selected subspace.")
    lines.append("- For each ciphertext output bit, we compute the Boolean ANF degree and coefficient weight.")
    lines.append("- Bits with low algebraic degree are more likely to be exploitable by interpolation-style methods.")
    lines.append("")

    for variable_byte, byte_results in results['results_by_byte'].items():
        lines.append(f"VARIABLE BYTE POSITION: {variable_byte}")
        lines.append("-" * 40)
        lines.append(f"Ciphertext bits tested: {byte_results['ciphertext_bits']}")
        lines.append(f"Max ANF degree observed: {byte_results['max_degree']}")
        lines.append(f"Min ANF degree observed: {byte_results['min_degree']}")
        lines.append(f"Average ANF degree: {byte_results['avg_degree']:.3f}")
        lines.append(f"Low-degree bit count (<= threshold): {byte_results['low_degree_count']} ({byte_results['low_degree_ratio']:.2%})")
        lines.append(f"Average ANF coefficient weight: {byte_results['avg_weight']:.1f} / {1 << results['sample_bits']}")
        lines.append(f"ANF degree histogram: {format_histogram(byte_results['degree_histogram'])}")
        lines.append(f"ANF weight histogram: {format_histogram(byte_results['weight_histogram'])}")
        lines.append("")

        if byte_results['low_degree_count'] == 0:
            lines.append("Result: No output bits with degree at or below threshold were found for this byte.")
        else:
            lines.append(
                f"Warning: {byte_results['low_degree_count']} ciphertext bit(s) had degree <= {byte_results['degree_threshold']}.")
            lines.append(
                "These output bits may be more vulnerable to low-degree interpolation analysis.")
            lines.append(f"Low-degree bit sample: {byte_results['low_degree_bits']}")
        lines.append("")

    lines.append("Note: This is a heuristic subspace analysis and does not constitute a full cryptanalysis proof.")
    lines.append("Consider testing multiple plaintext positions and larger subspaces for a more complete picture.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Interpolation attack heuristic test")
    parser.add_argument("--variable-bytes", default="0",
                        help="Comma-separated plaintext byte positions or ranges to test, e.g. 0,1-3")
    parser.add_argument("--degree-threshold", type=int, default=3,
                        help="Degree threshold for low-degree output bits")
    parser.add_argument("--sample-bits", type=int, default=8,
                        help="Number of plaintext bits to vary (sample size = 2^sample_bits)")
    parser.add_argument("--output", default=RESULT_FILE,
                        help="Output result file")
    args = parser.parse_args()

    variable_bytes = parse_variable_bytes(args.variable_bytes)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    results = run_interpolation_test(variable_bytes=variable_bytes,
                                     degree_threshold=args.degree_threshold,
                                     sample_bits=args.sample_bits)
    output = format_results(results)
    with open(args.output, 'w', encoding='utf-8') as out:
        out.write(output)
    print(f"Interpolation attack heuristic saved to {args.output}")


if __name__ == "__main__":
    main()
