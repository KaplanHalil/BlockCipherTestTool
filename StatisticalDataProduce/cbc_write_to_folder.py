import sys
import os
# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))
# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

import Alg as cipher
import utils

ciphertext_size= 25 # Mb


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

    key = [2]*cipher.mkey_size
    iv  = [1]*cipher.plaintext_size
    plaintext = [0]*(ciphertext_size * 1024 * 1024)


    cbc_encrypt_write(plaintext,key,iv)
