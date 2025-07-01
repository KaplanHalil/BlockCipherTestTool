"""
İmplementasyonun test sistemi ile uyumlu olmasi için aşağidaki fonksiyonlar formatiyla implementasyonda olmali 

state byte list leklinde olamali ve list üstünde islemler dönmeli [1,5,124,...,241] gibi

key schedule fonksiyonu keyi alip round keyleri 2d list olarak dondurmeli [[1,5,124,...,241],[1,5,124,...,241],...] gibi
"""

import sys
import os

# Add the utils directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
import utils

plaintext_size = 8  # bytes
ciphertext_size = 8  # bytes
mkey_size = 10  # bytes
round_key_size = 8  # bytes
round_key = 32 # number of subkeys
num_rounds = 31  # Number of full rounds (needs 32 round keys)

# Round constants storage
rc = [[0] * ciphertext_size for _ in range(num_rounds + 1)]

SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]

# Bit permutation table for PRESENT
PERM = [0, 16, 32, 48, 1, 17, 33, 49,
        2, 18, 34, 50, 3, 19, 35, 51,
        4, 20, 36, 52, 5, 21, 37, 53,
        6, 22, 38, 54, 7, 23, 39, 55,
        8, 24, 40, 56, 9, 25, 41, 57,
        10, 26, 42, 58, 11, 27, 43, 59,
        12, 28, 44, 60, 13, 29, 45, 61,
        14, 30, 46, 62, 15, 31, 47, 63]


def sub_bytes(state):
    nibble_state = utils.convert_to_nibble_array(state)  # 4-bit per half-byte
    for i in range(len(nibble_state)):
        nibble_state[i] = SBOX[nibble_state[i]]
    return utils.nibbles_to_int_array(nibble_state)


def permute(state):
    bit_state = utils.int_list_to_bit_list(state)
    new_bit_state = [0] * 64
    for i in range(64):
        new_bit_state[PERM[i]] = bit_state[i]
    return utils.bit_list_to_int_list(new_bit_state)


def add_round_key(state, round_key):
    return [s ^ k for s, k in zip(state, round_key)]


def key_schedule(key):
    keybits = utils.int_list_to_bit_list(key)  # 80 bits
    round_keys2d = []

    for i in range(num_rounds + 1):  # 32 round keys
        # Save first 64 bits as round key
        round_key_bits = keybits[:64]
        round_keys2d.append(utils.bit_list_to_int_list(round_key_bits))

        # Rotate 80-bit key left by 61 bits
        keybits = utils.rotate_left(keybits, 61)

        # Apply S-box to the leftmost 4 bits
        sbox_input = utils.bit_list_to_int(keybits[:4])
        sbox_output = SBOX[sbox_input]
        keybits[:4] = utils.int_to_bit_list(sbox_output, 4)

        # XOR round counter (i+1) with bits 60 to 64 and mask to 5 bits
        rc_segment = keybits[60:65]
        rc_value = utils.bit_list_to_int(rc_segment)
        rc_value = (rc_value ^ (i + 1)) & 0b11111
        keybits[60:65] = utils.int_to_bit_list(rc_value, 5)

    return round_keys2d



def encrypt(block, key, rc_store):
    round_keys = key_schedule(key)
    state = add_round_key(block, round_keys[0])
    #rc_store[0] = state

    for round in range(1, num_rounds + 1):  # 1 to 31
        state = sub_bytes(state)
        state = permute(state)
        state = add_round_key(state, round_keys[round])
        rc_store[round-1] = state

    return state

# Returns round ciphertexts
def return_rc(plaintext,key):

    rc=[[0]*ciphertext_size]*(num_rounds) # Define empty list to store round cipertexts
    encrypt(plaintext, key,rc)

    return rc


if __name__ == "__main__":
    plaintext = utils.str_to_int_array("0x0000000000000000")
    key = utils.str_to_int_array("0x00000000000000000000")

    print("Plaintext: ", utils.int_to_hex(plaintext))
    print("Key:       ", utils.int_to_hex(key))

    ciphertext = encrypt(plaintext, key, rc)

    print("Ciphertext:", utils.int_to_hex(ciphertext))  

    print(return_rc(plaintext, key))
