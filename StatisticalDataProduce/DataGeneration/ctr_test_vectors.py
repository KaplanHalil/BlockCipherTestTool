#!/usr/bin/env python3
import subprocess
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from ctr_write_to_folder import encrypt_ctr_chunk


def openssl_ctr_encrypt(key_hex: str, iv_hex: str, plaintext_hex: str) -> str:
    # OpenSSL requires binary input; use printf + xxd for hex to binary conversion.
    cmd = [
        'openssl', 'enc', '-aes-256-ctr', '-K', key_hex, '-iv', iv_hex,
    ]
    process = subprocess.run(cmd, input=bytes.fromhex(plaintext_hex), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise RuntimeError(f"OpenSSL failed: {process.stderr.decode('utf-8')}")
    return process.stdout.hex()


def main():
    # AES-256 CTR test vector
    key_hex = '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f'
    iv_hex = '000102030405060708090a0b0c0d0e0f'
    plaintext_hex = '00112233445566778899aabbccddeeffffeeddccbbaa99887766554433221100'

    key = bytes.fromhex(key_hex)
    iv = bytes.fromhex(iv_hex)
    plaintext = bytes.fromhex(plaintext_hex)

    expected_ciphertext_hex = openssl_ctr_encrypt(key_hex, iv_hex, plaintext_hex)
    computed_ciphertext = encrypt_ctr_chunk(plaintext, list(key), int.from_bytes(iv, 'big'), len(iv))
    computed_hex = computed_ciphertext.hex()

    print('Key :', key_hex)
    print('IV  :', iv_hex)
    print('PT  :', plaintext_hex)
    print('Expected CT:', expected_ciphertext_hex)
    print('Computed CT:', computed_hex)
    print()

    if computed_hex == expected_ciphertext_hex:
        print('CTR test vector PASSED')
        return 0
    else:
        print('CTR test vector FAILED')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
