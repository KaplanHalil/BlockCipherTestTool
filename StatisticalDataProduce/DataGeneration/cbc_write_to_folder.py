import argparse
import os
import sys

# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Algorithm'))
# Add the utils directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
# Add the StatisticalDataProduce/Tests directory so `statistical_tests` can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Tests'))

import Alg as cipher
import utils
from statistical_tests import run_all_tests, print_test_results


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def cbc_encrypt_write(plaintext, key, iv, output_file="ciphertext.hex", verbose=True):
    block_size = cipher.plaintext_size
    rc = [[0] * cipher.ciphertext_size for _ in range(cipher.num_rounds)]
    ciphertext = bytearray()
    previous_block = bytes(iv)
    total_size = len(plaintext)
    num_blocks = (total_size + block_size - 1) // block_size
    progress_interval = max(1, num_blocks // 100)

    for block_index in range(num_blocks):
        start = block_index * block_size
        end = start + block_size
        block = plaintext[start:end]

        if len(block) < block_size:
            block = block + bytes(block_size - len(block))

        xor_result = xor_bytes(block, previous_block)
        encrypted_block = cipher.encrypt(list(xor_result), key, rc)
        ciphertext.extend(encrypted_block)
        previous_block = bytes(encrypted_block)

        if verbose and (block_index % progress_interval == 0 or block_index == num_blocks - 1):
            progress = (block_index + 1) / num_blocks * 100
            print(f"Ciphertext progress: {progress:.2f}%", end='\r')

    with open(output_file, "wb") as f:
        f.write(ciphertext)

    if verbose:
        print("\nCiphertext generation complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="Fast CBC ciphertext generation for statistical tests")
    parser.add_argument("--size-mb", type=int, default=4,
                        help="Ciphertext size in MiB (default: 4)")
    parser.add_argument("--output", default="ciphertext.hex",
                        help="Output ciphertext filename")
    parser.add_argument("--skip-analysis", action="store_true",
                        help="Only generate ciphertext and skip running statistical tests")
    parser.add_argument("--quiet", action="store_true",
                        help="Reduce console output during generation")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    key = [2] * cipher.mkey_size
    iv = bytes([1] * cipher.plaintext_size)
    plaintext = bytearray(args.size_mb * 1000 * 1000)  # Generate plaintext of the specified size

    cbc_encrypt_write(plaintext, key, iv, output_file=args.output, verbose=not args.quiet)

    if args.skip_analysis:
        print(f"Generated ciphertext saved as {args.output}")
    else:
        print("Reading ciphertext and running statistical tests...")
        with open(args.output, "rb") as f:
            ciphertext_data = f.read()

        results = run_all_tests(ciphertext_data)
        print_test_results(results)
