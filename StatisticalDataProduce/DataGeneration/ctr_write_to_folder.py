import argparse
import os
import sys
import concurrent.futures

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


def create_counter_block(counter_value, block_size):
    return counter_value.to_bytes(block_size, byteorder='big')


def ctr_encrypt_block(plain_block, key, counter_value, block_size):
    counter_block = create_counter_block(counter_value, block_size)
    encrypted_counter = cipher.encrypt(list(counter_block), key, [[0] * cipher.ciphertext_size for _ in range(cipher.num_rounds)])
    encrypted_counter = bytes(encrypted_counter)
    if len(plain_block) < block_size:
        plain_block = plain_block + bytes(block_size - len(plain_block))
    return xor_bytes(plain_block, encrypted_counter)


def encrypt_ctr_chunk(chunk_data, key, start_counter, block_size):
    ciphertext = bytearray()
    num_blocks = (len(chunk_data) + block_size - 1) // block_size
    for block_index in range(num_blocks):
        start = block_index * block_size
        end = start + block_size
        block = chunk_data[start:end]
        counter_value = start_counter + block_index
        ciphertext.extend(ctr_encrypt_block(block, key, counter_value, block_size))
    return bytes(ciphertext)


def ctr_encrypt_write(plaintext, key, iv, output_file="Results/ciphertext.hex", verbose=True, workers=1):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    block_size = cipher.plaintext_size
    total_size = len(plaintext)
    num_blocks = (total_size + block_size - 1) // block_size
    progress_interval = max(1, num_blocks // 100)
    start_counter = int.from_bytes(iv, byteorder='big')

    if workers is None or workers <= 1:
        ciphertext = bytearray()
        for block_index in range(num_blocks):
            start = block_index * block_size
            end = start + block_size
            block = plaintext[start:end]
            counter_value = start_counter + block_index
            ciphertext.extend(ctr_encrypt_block(block, key, counter_value, block_size))

            if verbose and (block_index % progress_interval == 0 or block_index == num_blocks - 1):
                progress = (block_index + 1) / num_blocks * 100
                print(f"Ciphertext progress: {progress:.2f}%", end='\r')

        with open(output_file, "wb") as f:
            f.write(ciphertext)

        if verbose:
            print("\nCiphertext generation complete.")
        return

    workers = min(workers, num_blocks)
    chunk_blocks = num_blocks // workers
    chunk_ranges = []
    start_block = 0

    for i in range(workers):
        end_block = start_block + chunk_blocks
        if i == workers - 1:
            end_block = num_blocks
        chunk_ranges.append((start_block, end_block, i))
        start_block = end_block

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = []
        for chunk_start, chunk_end, chunk_id in chunk_ranges:
            start = chunk_start * block_size
            end = chunk_end * block_size
            chunk_data = plaintext[start:end]
            chunk_counter = start_counter + chunk_start
            futures.append((chunk_id, executor.submit(encrypt_ctr_chunk, chunk_data, key, chunk_counter, block_size)))

        chunk_results = [None] * len(chunk_ranges)
        for chunk_id, future in sorted(futures, key=lambda item: item[0]):
            chunk_results[chunk_id] = future.result()

    with open(output_file, "wb") as f:
        for chunk_data in chunk_results:
            f.write(chunk_data)

    if verbose:
        print("\nParallel CTR ciphertext generation complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="Fast CTR ciphertext generation for statistical tests")
    parser.add_argument("--size-mb", type=int, default=4,
                        help="Ciphertext size in MiB (default: 4)")
    parser.add_argument("--output", default="Results/ciphertext.hex",
                        help="Output ciphertext filename")
    parser.add_argument("--skip-analysis", action="store_true",
                        help="Only generate ciphertext and skip running statistical tests")
    parser.add_argument("--quiet", action="store_true",
                        help="Reduce console output during generation")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of worker processes for parallel CTR generation")
    parser.add_argument("--nonce", default=None,
                        help="Optional nonce / initial counter value as hex string")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    key = [2] * cipher.mkey_size
    iv = bytes([1] * cipher.plaintext_size)
    if args.nonce is not None:
        nonce = args.nonce
        if nonce.startswith('0x') or nonce.startswith('0X'):
            nonce = nonce[2:]
        iv = bytes.fromhex(nonce.ljust(cipher.plaintext_size * 2, '0')[:cipher.plaintext_size * 2])

    plaintext = bytearray(args.size_mb * 1000 * 1000)  # Generate plaintext of the specified size

    ctr_encrypt_write(plaintext, key, iv, output_file=args.output, verbose=not args.quiet, workers=args.workers)

    if args.skip_analysis:
        print(f"Generated ciphertext saved as {args.output}")
    else:
        print("Reading ciphertext and running statistical tests...")
        with open(args.output, "rb") as f:
            ciphertext_data = f.read()

        results = run_all_tests(ciphertext_data)
        print_test_results(results)
