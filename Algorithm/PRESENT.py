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

plaintext_size = 8  #bytes
ciphertext_size = 8  #bytes
mkey_size= 32 #bytes
round_key_size = 16 #bytes
round_key = 15 # number of subkeys
num_rounds = 31

rc=[[0]*ciphertext_size]*num_rounds # Define empty list to store round cipertexts

SBOX = [
    0xC, 0x5, 0x6 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2
]

PERM = [0, 16, 32, 48, 1, 17, 33, 49, 2, 18, 34, 50, 3, 19, 35, 51, 4, 20, 36, 52, 5, 21, 37, 53, 6, 22, 38, 54, 7, 23, 39, 55,
        8, 24, 40, 56, 9, 25, 41, 57, 10, 26, 42, 58, 11, 27, 43, 59, 12, 28, 44, 60, 13, 29, 45, 61, 14, 30, 46, 62, 15, 31, 47, 63]

def sub_bytes(state):
    return [SBOX[byte] for byte in state]

def add_round_key(state, round_key):
    return [state[i] ^ round_key[i] for i in range(len(state))]

def permute(state): 

    bit_state=utils.int_list_to_bit_list(state)
    for i in range(len(PERM)):
        bit_state[i] = bit_state(PERM[i])

    return utils.bit_list_to_int_list(bit_state)

# Takes mk and returns round keys as 2d list
def key_schedule(key):
    keybits = utils.int_list_to_bit_list(key)
    round_keys2d = []
    round_keys2d.append(keybits[:64])  # Initial key as the first round key
    for i in range(round_key):
        keybits=utils.rotate_left(keybits, 61)  # Rotate left by 61 bits
        first4 = keybits[:4]
        nibble = utils.bit_list_to_int_list(first4)
        sbox_output = SBOX[nibble]
        new_first4 = utils.int_to_bit_list(sbox_output, 4) 
        keybits = new_first4 + keybits[4:]  # Replace first 4 bits with SBOX output
        
        round_keys2d.append(keybits[:64])  # Append the new round key
    return []

def encrypt(block, key,rc):

    round_keys = key_schedule(key)
    state = add_round_key(block, round_keys[0])

    for round in range(1, num_rounds):
        
        state = sub_bytes(state)
        
        rc[round-1]=state # Store round ciphertexts
            
    state = sub_bytes(state)
    

    rc[num_rounds-1]=state # Store last round ciphertexts

    return state

if __name__ == "__main__":

    
    plaintext = utils.str_to_int_array("0x0000000000000000")
    key = utils.str_to_int_array("0x00000000000000000000")
    
    print("plaintext:",utils.int_to_hex(plaintext))
    print("key:",utils.int_to_hex(key))

    ciphertext = encrypt(plaintext, key,rc)
    
    print("Ciphertext:", utils.int_to_hex(ciphertext))