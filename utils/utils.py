from PIL import Image

# Takes string of form "0x0001..." converts int list of form [0,1]
def str_to_int_array(hex_str):
    # Remove the '0x' prefix if it exists
    hex_str = hex_str[2:] if hex_str.startswith("0x") else hex_str
    
    # Ensure the length of the string is even for grouping into bytes
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str  # Add leading zero if necessary
    
    # Convert each pair of characters into a byte (integer)
    return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]

# Takes int array converts hex array
def int_to_hex(int_list):
    ciphertext_hex_array = [f"0x{byte:02x}" for byte in int_list]
    formatted_ciphertext = "[" + ", ".join(ciphertext_hex_array) + "]"
    return formatted_ciphertext

# Galois Field multiplication
def gmul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        a = (a << 1) ^ (0x1B if a & 0x80 else 0)
        b >>= 1
    return p & 0xFF  # Ensure the result is a byte

# XOR operation
def xor_blocks(block1, block2):
    return [b1 ^ b2 for b1, b2 in zip(block1, block2)]

# Convert 2D list of integers into a 2D list of bit arrays
def convert_to_2d_bit_list(two_dim_list):
    bit_list = []
    for row in two_dim_list:
        flat_bit_row = []
        for num in row:
            flat_bit_row.extend(map(int, f"{num:08b}"))
        bit_list.append(flat_bit_row)
    return bit_list

# Convert int list to bit list
def int_list_to_bit_list(int_list):
    return [bit for num in int_list for bit in map(int, f"{num:08b}")]

# Convert bit list to int list
def bit_list_to_int_list(bit_list):
    if len(bit_list) % 8 != 0:
        raise ValueError("The length of the bit list must be a multiple of 8.")
    return [int("".join(map(str, bit_list[i:i + 8])), 2) for i in range(0, len(bit_list), 8)]

# XOR two 2D lists
def xor_2d_lists(list1, list2):
    if len(list1) != len(list2) or any(len(row1) != len(row2) for row1, row2 in zip(list1, list2)):
        raise ValueError("The dimensions of the two 2D lists must match.")
    return [[x ^ y for x, y in zip(row1, row2)] for row1, row2 in zip(list1, list2)]

# Sum two 2D lists
def sum_2d_lists(list1, list2):
    if len(list1) != len(list2) or any(len(row1) != len(row2) for row1, row2 in zip(list1, list2)):
        raise ValueError("The dimensions of the two 2D lists must match.")
    return [[x + y for x, y in zip(row1, row2)] for row1, row2 in zip(list1, list2)]

# Convert 2D list to 1D list
def convert_2d_list_to_1d(two_d_list):
    return [item for sublist in two_d_list for item in sublist]


def create_image_from_2d_list(data):
    width, height = len(data[0]), len(data)
    img = Image.new("RGB", (width, height), "black")
    pixels = img.load()
    
    color_map = {
        0: (255, 255, 255),  # White
        2: (0, 153, 76),      # Green
        4: (204, 204, 0),      # Yellow
        6: (255, 128, 0),    # Orange
        8: (255, 0, 0),      # Red
        10: (204, 0, 0),      # Red
        12: (153, 0, 0),      # Red
        16: (139, 69, 19)     # Brown
    }
    
    for y in range(height):
        for x in range(width):
            pixels[x, y] = color_map.get(data[y][x], (0, 0, 0))  # Default to black if value not in map
    
    return img

def rotate_left(lst, nekadar):
    """
    Rotates a list 61 positions to the left (circularly).
    
    :param lst: List of elements (e.g., bits)
    :return: Rotated list
    """
    n = len(lst)
    return lst[nekadar % n:] + lst[:nekadar % n]


def int_to_bit_list(n, width):
    """
    Converts an integer to a list of bits with the specified width.
    
    :param n: Integer value (non-negative)
    :param width: Number of bits in the output list
    :return: List[int] of 0s and 1s
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n >= (1 << width):
        raise ValueError(f"Integer too large to fit in {width} bits")
    
    return [int(b) for b in f"{n:0{width}b}"]

def bit_list_to_int(bits):
    return int(''.join(map(str, bits)), 2)

# int array alıp 4 bitlik nipple array veren fonk.
def convert_to_nibble_array(int_array):
    nibble_array = []
    for val in int_array:
        bits = int_to_bit_list(val, 8)  # Convert to 8-bit binary list
        left_nibble = bit_list_to_int(bits[:4])   # First 4 bits
        right_nibble = bit_list_to_int(bits[4:])  # Last 4 bits
        nibble_array.append(left_nibble)
        nibble_array.append(right_nibble)
    return nibble_array

# 4 bitlik nipple array alıp int array veren fonksiyon
def nibbles_to_int_array(nibble_array):
    if len(nibble_array) % 2 != 0:
        raise ValueError("Nibble array length must be even.")
    
    int_array = []
    for i in range(0, len(nibble_array), 2):
        left = nibble_array[i]     # high 4 bits
        right = nibble_array[i+1]  # low 4 bits
        combined = (left << 4) | right
        int_array.append(combined)
    return int_array



if __name__ == "__main__":

    nibbles = [10, 11, 3, 4, 15, 15]
    reconstructed = nibbles_to_int_array(nibbles)
    print("Nibbles:", nibbles)
    print("Reconstructed ints:", reconstructed)

