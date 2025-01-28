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

def convert_to_2d_bit_list(two_dim_list):
    """
    Converts a 2D list of 8-bit integers into a 2D list of 128-bit flat lists.

    Args:
        two_dim_list (list[list[int]]): A 2D list of integers.

    Returns:
        list[list[int]]: A 2D list where each row contains 128 bits.
    """
    bit_list = []
    for row in two_dim_list:
        flat_bit_row = []
        for num in row:
            flat_bit_row.extend(map(int, f"{num:08b}"))
        bit_list.append(flat_bit_row)
    return bit_list


def int_list_to_bit_list(int_list):
    """
    Converts a list of integers into a flat list of bits, with each integer represented by 8 bits.

    Args:
        int_list (list[int]): A list of integers.

    Returns:
        list[int]: A flat list of bits.
    """
    bit_list = []
    for num in int_list:
        bit_list.extend(map(int, f"{num:08b}"))
    return bit_list



def bit_list_to_int_list(bit_list):
    """
    Converts a flat list of bits into a list of integers, where each integer
    is formed from 8 bits.

    Args:
        bit_list (list[int]): A flat list of bits (0s and 1s).

    Returns:
        list[int]: A list of integers converted from the bit chunks.
    """
    if len(bit_list) % 8 != 0:
        raise ValueError("The length of the bit list must be a multiple of 8.")
    
    int_list = []
    for i in range(0, len(bit_list), 8):
        byte = bit_list[i:i + 8]  # Take 8 bits
        integer = int("".join(map(str, byte)), 2)  # Convert bits to integer
        int_list.append(integer)
    return int_list

def xor_2d_lists(list1, list2):
    """
    Takes two 2D lists of integers, XORs their corresponding elements, and returns the result.

    Args:
        list1 (list[list[int]]): The first 2D list of integers.
        list2 (list[list[int]]): The second 2D list of integers.

    Returns:
        list[list[int]]: A 2D list with XORed values.

    Raises:
        ValueError: If the dimensions of the two lists don't match.
    """
    if len(list1) != len(list2) or any(len(row1) != len(row2) for row1, row2 in zip(list1, list2)):
        raise ValueError("The dimensions of the two 2D lists must match.")

    result = []
    for row1, row2 in zip(list1, list2):
        result.append([x ^ y for x, y in zip(row1, row2)])
    return result

def sum_2d_lists(list1, list2):
    """
    Takes two 2D lists of integers, sums their corresponding elements, and returns the result.

    Args:
        list1 (list[list[int]]): The first 2D list of integers.
        list2 (list[list[int]]): The second 2D list of integers.

    Returns:
        list[list[int]]: A 2D list with summed values.

    Raises:
        ValueError: If the dimensions of the two lists don't match.
    """
    if len(list1) != len(list2) or any(len(row1) != len(row2) for row1, row2 in zip(list1, list2)):
        raise ValueError("The dimensions of the two 2D lists must match.")

    result = []
    for row1, row2 in zip(list1, list2):
        result.append([x + y for x, y in zip(row1, row2)])
    return result


def convert_2d_list_to_1d(two_d_list):
    """
    Converts a 2D list into a 1D list.

    :param two_d_list: List of lists (2D list)
    :return: Flattened 1D list
    """
    return [item for sublist in two_d_list for item in sublist]

if __name__ == "__main__":

    unique_strings = []

    # Generate 10,000 unique strings
    for i in range(10000):
        # Convert the counter `i` to a hexadecimal string with zero-padding
        hex_value = ''.join(f"{(i + j) % 256:02x}" for j in range(32))
        unique_string = f"0x{hex_value}"
        unique_strings.append(unique_string)

    # Optional: Print the first 10 strings as a preview
    for string in unique_strings[:10]:
        print(string)

    # If you want to save these strings to a file, uncomment the following lines:
    # with open("unique_strings.txt", "w") as f:
    #     f.write("\n".join(unique_strings))


