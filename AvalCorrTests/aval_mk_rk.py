"""
mk-rk Aval Test

Rasgele 1000 adet mk alir ve her bir bitini tek tek değiştirip round keyleri hesaplar.
Genel beklenti rk'daki her bit bitin 450-550 arasında değişmesidir.
Buna göre convert_2d_list fonksiyonunda 255 beyaz 0 siyah olacak şekilde piksellere renk atar.
Çikti olarak verdiği resimde sol taraf mk bitleri üst raraf rk bitleri.


"""

from PIL import Image
import sys
import os

# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))
# Add the utils directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

import Alg as cipher
import utils
import time
from multiprocessing import Pool
import argparse

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
results_dir = os.path.join(root_dir, 'Results')
os.makedirs(results_dir, exist_ok=True)



# takes 2d list and converts it to 1d list
def convert_2d_list(input_list):
    def convert_value(value):
        if 0 <= value < 300:
            return 0
        elif 300 <= value < 350:
            return 50
        elif 350 <= value < 400:
            return 100
        elif 400 <= value < 450:
            return 150
        elif 450 <= value < 550:
            return 255
        elif 550 <= value < 600:
            return 210
        elif 600 <= value < 700:
            return 150
        elif 700 <= value < 800:
            return 100
        elif 800 <= value < 900:
            return 50
        elif 900 <= value <= 1000:
            return 0
        else:
            raise ValueError(f"Value {value} is out of range 0-1000.")

    return [convert_value(value) for row in input_list for value in row]


def draw_round_key_lines(img, line_color=128):
    """Draw vertical lines to distinguish between round keys"""
    pixels = img.load()
    round_key_width = cipher.round_key_size * 8
    
    for round_num in range(1, cipher.round_key):
        x_pos = round_num * round_key_width
        for y in range(img.size[1]):
            pixels[x_pos, y] = line_color


def process_bit_mk_rk(bit_index):
    """Process a single bit index for mk-rk avalanche test"""
    # Define empty list to store result
    result = [[0 for _ in range(cipher.round_key_size*8)] for _ in range(cipher.round_key)]
    
    # Generate 1000 unique keys
    for k in range(1000):
    
        # Convert the counter `k` to a hexadecimal string with zero-padding
        hex_value = ''.join(f"{(k + j) % 256:02x}" for j in range(cipher.mkey_size))
        unique_key = f"0x{hex_value}"

        mkey = utils.str_to_int_array(unique_key)

        mkey_bits=utils.int_list_to_bit_list(mkey)

        rkeys=cipher.key_schedule(mkey)

        rkeys_bits = utils.convert_to_2d_bit_list(rkeys)

        # change value of bit
        mkey_bits[bit_index] = mkey_bits[bit_index]^1
        # Compute new mk and rk
        new_mkey = utils.bit_list_to_int_list(mkey_bits)
        new_rkeys=cipher.key_schedule(new_mkey)
        new_rkeys_bits = utils.convert_to_2d_bit_list(new_rkeys)
        # xor new and old rk to find different bits
        fark=utils.xor_2d_lists(rkeys_bits,new_rkeys_bits)
        # accumilate different bits
        result=utils.sum_2d_lists(result,fark)

    return bit_index, convert_2d_list(result)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run master-key to round-keys avalanche test')
    parser.add_argument('--workers', type=int, default=None, help='Number of worker processes')
    args = parser.parse_args()
    
    # Start timing
    a = time.time()
    
    # Setup parallel processing
    num_workers = args.workers if args.workers else None
    
    # Create output image: (round_key_bits_total, master_key_bits)
    img = Image.new('L', 
                    (cipher.round_key_size*8*cipher.round_key, cipher.mkey_size*8),
                    "black")
    pixels = img.load()

    # Test each master key bit in parallel
    bit_indices = range(cipher.mkey_size * 8)
    
    print(f"Testing {cipher.mkey_size*8} master key bits (key schedule) in parallel...")
    with Pool(processes=num_workers) as pool:
        results = pool.map(process_bit_mk_rk, bit_indices)
    
    # Fill in the image from results
    for bit_index, draw_list in results:
        for j in range(img.size[0]):
            pixels[j, bit_index] = draw_list[j]

    # Add visual separators
    draw_round_key_lines(img)

    # Save result
    img.save(os.path.join(results_dir, "aval_mk-rk.png"))
    b = time.time()
    print(f"Time of aval mk-rk: {(b-a)/60:.2f} minutes")
