
import sys
import os
# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))
# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

import Alg as cipher
import utils

ciphertext_size= 99 # Mb


# makes CBC mode encryption and writes ciphertext to the file
def cbc_encrypt_write(plaintext, key, iv):

    rc=[[0]*ciphertext_size]*cipher.num_rounds # Define empty list to store round cipertexts

    # Encrypt and write the plaintext in chunks
    with open("ciphertext.hex", "wb") as f:
        previous_block = iv
        for i in range(0, len(plaintext), cipher.plaintext_size):
            block = plaintext[i:i + cipher.plaintext_size]
            if len(block) < cipher.plaintext_size:
                block += [0] * (cipher.plaintext_size - len(block))
            xor_result = utils.xor_blocks(block, previous_block)
            encrypted_block = cipher.encrypt(xor_result, key,rc)
            f.write(bytes(encrypted_block))
            previous_block = encrypted_block
            # Print progress
            progress = (i + cipher.plaintext_size) / len(plaintext) * 100
            print(f"Ciphertext progress: {progress:.2f}%", end='\r')

    

if __name__ == "__main__":

    key = utils.str_to_int_array("0x603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")
    iv  = utils.str_to_int_array("0x000102030405060708090A0B0C0D0E0F")
    
    # Generate plaintext
    #plaintext = [(i % 256) for i in range(ciphertext_size * 1024 * 1024)]
    # Choose plaintext
    plaintext = [0]*(ciphertext_size * 1024 * 1024)

    cbc_encrypt_write(plaintext,key,iv)
