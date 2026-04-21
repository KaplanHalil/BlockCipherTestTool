#!/usr/bin/env python3
"""Interpolation resistance analysis for block cipher round outputs.

This script performs a heuristic interpolation analysis of a block cipher.
It is not a complete cryptanalytic attack, but it helps identify whether
selected ciphertext output bytes can be modeled by low-degree polynomials
from a chosen plaintext subspace.

How it works:
- Choose one plaintext byte position to vary over a random sample.
- Fix the remaining plaintext bytes and the key to constant values.
- Encrypt the block and collect the round outputs from the cipher's rc storage.
- For each round output byte, build a mapping from the chosen plaintext byte
  to the output byte value.
- Use Lagrange interpolation over GF(2^8) to compute a polynomial for each
  output byte.
- Analyze polynomial degree and coefficient density for each round and byte.

Why this matters:
- Interpolation-style attacks attempt to model ciphertext bits as algebraic
  polynomials of plaintext bits.
- Lower polynomial degree and sparse coefficient support can make algebraic
  analysis easier.

Limitations:
- This is a heuristic subspace analysis, not a complete attack.
- Results depend on the chosen plaintext byte, the fixed values, and the
  number of random samples.
"""

import argparse
import os
import sys
import concurrent.futures

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))

import Alg as cipher

RESULT_FILE = "Results/interpolation_attack_test.txt"


def encode_byte_values(data):
    return [int(bit) for byte in data for bit in format(byte, '08b')]


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


def gf_add(a, b):
    return a ^ b


def gf_mul(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= 0x1B
        b >>= 1
    return result


def gf_pow(a, power):
    result = 1
    while power:
        if power & 1:
            result = gf_mul(result, a)
        a = gf_mul(a, a)
        power >>= 1
    return result


def gf_inv(a):
    if a == 0:
        raise ZeroDivisionError("GF inverse of zero")
    return gf_pow(a, 254)


def poly_add(a, b):
    length = max(len(a), len(b))
    result = [0] * length
    for i in range(length):
        if i < len(a):
            result[i] ^= a[i]
        if i < len(b):
            result[i] ^= b[i]
    return result


def poly_mul(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] ^= gf_mul(ai, bj)
    return result


def lagrange_interpolate(points):
    if not points:
        return [0]
    coeffs = [0]
    for i, (xi, yi) in enumerate(points):
        numerator = [1]
        denominator = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            numerator = poly_mul(numerator, [gf_add(0, xj), 1])
            denominator = gf_mul(denominator, gf_add(xi, xj))
        factor = gf_mul(yi, gf_inv(denominator))
        term = [gf_mul(c, factor) for c in numerator]
        coeffs = poly_add(coeffs, term)
    return coeffs


def encrypt_block(plaintext, key):
    rc = [[0] * cipher.ciphertext_size for _ in range(cipher.num_rounds)]
    ciphertext = cipher.encrypt(list(plaintext), key, rc)
    return bytes(ciphertext), rc


def run_interpolation_test(variable_byte, sample_count=1000, fixed_byte_value=0, parallel=False, workers=None):
    if variable_byte < 0 or variable_byte >= cipher.plaintext_size:
        raise ValueError(f"variable_byte {variable_byte} is out of range")

    key = [0] * cipher.mkey_size
    fixed_plaintext = bytearray([fixed_byte_value] * cipher.plaintext_size)
    random_values = __import__('random').sample(range(256), min(sample_count, 256))

    round_mappings = [ {byte_index: {} for byte_index in range(cipher.ciphertext_size)} for _ in range(cipher.num_rounds) ]

    for value in random_values:
        plaintext = fixed_plaintext.copy()
        plaintext[variable_byte] = value
        _, rc = encrypt_block(plaintext, key)
        for round_index, round_output in enumerate(rc):
            for byte_index, output_byte in enumerate(round_output):
                round_mappings[round_index][byte_index][value] = output_byte

    all_round_results = []
    for round_index, byte_mappings in enumerate(round_mappings):
        byte_stats = compute_byte_stats_for_round(round_index, byte_mappings, parallel=parallel, workers=workers)
        all_round_results.append({
            'round_index': round_index + 1,
            'byte_stats': byte_stats,
        })

    return {
        'variable_byte': variable_byte,
        'sample_count': len(random_values),
        'round_results': all_round_results,
    }


def format_histogram(histogram, max_line_length=90):
    if not histogram:
        return "None"

    items = [f"{k}:{v}" for k, v in histogram.items()]
    lines = []
    current_line = ""
    for item in items:
        if current_line:
            next_line = f"{current_line}, {item}"
        else:
            next_line = item

        if len(next_line) > max_line_length and current_line:
            lines.append(current_line)
            current_line = item
        else:
            current_line = next_line

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def compute_byte_stat(task):
    round_index, byte_index, mapping = task
    if not mapping:
        return {
            'round_index': round_index,
            'byte_index': byte_index,
            'sample_size': 0,
            'max_degree': None,
            'weight': None,
            'sparsity': None,
            'degree_histogram': {},
            'coeff_histogram': {},
        }

    points = sorted(mapping.items())
    coefficients = lagrange_interpolate(points)
    nonzero = [(i, c) for i, c in enumerate(coefficients) if c != 0]
    degree = max((i for i, _ in nonzero), default=0)
    weight = len(nonzero)
    sparsity = weight / len(coefficients)

    return {
        'round_index': round_index,
        'byte_index': byte_index,
        'sample_size': len(points),
        'max_degree': degree,
        'weight': weight,
        'sparsity': sparsity,
        'degree_histogram': build_histogram([i for i, _ in nonzero]),
        'coeff_histogram': build_histogram([c for _, c in nonzero]),
    }


def compute_byte_stats_for_round(round_index, byte_mappings, parallel=False, workers=None):
    tasks = [(round_index, byte_index, byte_mappings[byte_index]) for byte_index in range(cipher.ciphertext_size)]

    if parallel:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            byte_stats = list(executor.map(compute_byte_stat, tasks))
    else:
        byte_stats = [compute_byte_stat(task) for task in tasks]

    return sorted(byte_stats, key=lambda item: item['byte_index'])


def format_results(results):
    lines = []
    lines.append("INTERPOLATION ATTACK ANALYSIS")
    lines.append("========================================")
    lines.append(f"Variable plaintext byte position: {results['variable_byte']}")
    lines.append(f"Random sample count: {results['sample_count']}")
    lines.append("")
    lines.append("Test description:")
    lines.append("- One plaintext byte is randomly varied over the selected subspace.")
    lines.append("- The remaining plaintext bytes and the key remain fixed.")
    lines.append("- The cipher is executed and round outputs are collected from rc.")
    lines.append("- Each round output byte is treated as an 8-bit function of the selected input byte.")
    lines.append("- For each output byte and round, we compute a Lagrange interpolating polynomial over GF(2^8).")
    lines.append("- We analyze polynomial degree and coefficient sparsity for each round and byte.")
    lines.append("")

    for round_result in results['round_results']:
        lines.append(f"ROUND {round_result['round_index']}")
        lines.append("-" * 40)
        for byte_stat in round_result['byte_stats']:
            lines.append(f"Output byte {byte_stat['byte_index']}:")
            lines.append(f"  Samples used: {byte_stat['sample_size']}")
            if byte_stat['sample_size'] == 0:
                lines.append("  No samples available for this output byte.")
                continue
            lines.append(f"  Max polynomial degree: {byte_stat['max_degree']}")
            lines.append(f"  Coefficient count: {byte_stat['weight']}")
            lines.append(f"  Coefficient sparsity: {byte_stat['sparsity']:.3f}")
            lines.append("  Degree histogram:")
            lines.extend(f"    {line}" for line in format_histogram(byte_stat['degree_histogram']).split('\n'))
            lines.append("  Coefficient histogram:")
            lines.extend(f"    {line}" for line in format_histogram(byte_stat['coeff_histogram']).split('\n'))
        lines.append("")

    lines.append("Summary:")
    lines.append("- Lower max degree and lower coefficient density can indicate easier interpolation attack structure.")
    lines.append("- Dense or high-degree polynomials suggest stronger algebraic complexity.")
    lines.append("- This is a heuristic subspace analysis and does not replace a full cryptanalysis.")
    return "\n".join(lines) + "\n"


def format_summary(results):
    lines = []
    lines.append("INTERPOLATION ATTACK SUMMARY")
    lines.append("============================")
    lines.append(f"Variable plaintext byte position: {results['variable_byte']}")
    lines.append(f"Random sample count: {results['sample_count']}")
    lines.append("")

    all_degrees = []
    all_weights = []
    all_sparsities = []
    total_bytes = 0

    for round_result in results['round_results']:
        for byte_stat in round_result['byte_stats']:
            if byte_stat['sample_size'] > 0:
                all_degrees.append(byte_stat['max_degree'])
                all_weights.append(byte_stat['weight'])
                all_sparsities.append(byte_stat['sparsity'])
                total_bytes += 1

    if total_bytes == 0:
        lines.append("No data available for summary.")
        return "\n".join(lines) + "\n"

    avg_degree = sum(all_degrees) / len(all_degrees)
    avg_weight = sum(all_weights) / len(all_weights)
    avg_sparsity = sum(all_sparsities) / len(all_sparsities)
    max_degree = max(all_degrees)
    min_degree = min(all_degrees)

    lines.append(f"Total output bytes analyzed: {total_bytes}")
    lines.append(f"Average max polynomial degree: {avg_degree:.2f}")
    lines.append(f"Maximum degree across all: {max_degree}")
    lines.append(f"Minimum degree across all: {min_degree}")
    lines.append(f"Average coefficient count: {avg_weight:.2f}")
    lines.append(f"Average coefficient sparsity: {avg_sparsity:.3f}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Lower average degree suggests easier algebraic modeling.")
    lines.append("- Higher sparsity indicates fewer non-zero coefficients.")
    lines.append("- This summary provides an overview; refer to detailed results for per-byte analysis.")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Interpolation attack test using random input subspace and round outputs")
    parser.add_argument("--variable-byte", type=int, default=0,
                        help="Plaintext byte position to vary (default 0)")
    parser.add_argument("--sample-count", type=int, default=1000,
                        help="Number of random values for the selected byte")
    parser.add_argument("--parallel", action='store_true',
                        help="Compute interpolation stats in parallel using multiple processes")
    parser.add_argument("--workers", type=int, default=None,
                        help="Number of worker processes for parallel execution")
    parser.add_argument("--output", default=RESULT_FILE,
                        help="Output result file for detailed results")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    results = run_interpolation_test(
        args.variable_byte,
        sample_count=args.sample_count,
        parallel=args.parallel,
        workers=args.workers,
    )
    detailed_output = format_results(results)
    with open(args.output, 'w', encoding='utf-8') as out:
        out.write(detailed_output)
    print(f"Detailed interpolation attack analysis saved to {args.output}")

    summary_output = format_summary(results)
    summary_file = args.output.replace('.txt', '_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as out:
        out.write(summary_output)
    print(f"Interpolation attack summary saved to {summary_file}")


if __name__ == "__main__":
    main()
