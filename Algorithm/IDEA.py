
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
mkey_size= 16 #bytes
round_key_size = 16 #bytes
round_key = 15 # number of subkeys
num_rounds = 14

rc=[[0]*ciphertext_size]*num_rounds # Define empty list to store round cipertexts

SBOX = [0x63, 0x7c, 0x77, ...]
PERM = [0, 16, 32, 48, 1, 17, 33, 49,...]

def sub_bytes(state):
    return [SBOX[byte] for byte in state]

def permute(state):
    new_state = [0] * len(state)
    for i in range(len(state)):
        new_state[PERM[i]] = state[i]
    return new_state

def add_round_key(state, round_key):
    return [state[i] ^ round_key[i] for i in range(len(state))]

# Takes mk and returns round keys as 2d list
def key_schedule(key):
    
    return []

def encrypt(block, key,rc):

    round_keys = key_schedule(key)
    state = add_round_key(block, round_keys[0])

    for round in range(1, num_rounds):
        
        state = sub_bytes(state)
        state = permute(state)
        state = add_round_key(state, round_keys[round])
        
        rc[round-1]=state # Store round ciphertexts
            
    state = sub_bytes(state)
    

    rc[num_rounds-1]=state # Store last round ciphertexts

    return state

# Returns round ciphertexts
def return_rc(plaintext,key):

    rc=[[0]*ciphertext_size]*num_rounds # Define empty list to store round cipertexts
    encrypt(plaintext, key,rc)

    return rc

if __name__ == "__main__":

    
    plaintext = utils.str_to_int_array("0x00112233445566778899aabbccddeeff")
    key = utils.str_to_int_array("0x000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
    
    print("plaintext:",utils.int_to_hex(plaintext))
    print("key:",utils.int_to_hex(key))

    ciphertext = encrypt(plaintext, key,rc)
    
    print("Ciphertext:", utils.int_to_hex(ciphertext))