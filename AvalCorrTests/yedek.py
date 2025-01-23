import utils
import AES_256 as cipher

mkey_size= 32 #bytes
round_key_size = 16 #bytes
round_key = 15 # number of subkeys

def convert_2d_list(input_list):
    def convert_value(value):
        if 0 <= value < 100:
            return 0
        elif 100 <= value < 200:
            return 50
        elif 200 <= value < 300:
            return 100
        elif 300 <= value < 400:
            return 150
        elif 400 <= value < 600:
            return 255
        elif 600 <= value < 700:
            return 150
        elif 700 <= value < 800:
            return 100
        elif 800 <= value < 900:
            return 50
        elif 900 <= value < 1000:
            return 0
        else:
            raise ValueError(f"Value {value} is out of range 0-1000.")

    return [[convert_value(value) for value in row] for row in input_list]

if __name__ == "__main__":

    # Generate 100 unique keys
    for k in range(100):
        
        # Convert the counter `k` to a hexadecimal string with zero-padding
        hex_value = ''.join(f"{(k + j) % 256:02x}" for j in range(32))
        unique_string = f"0x{hex_value}"
    
        mkey = utils.str_to_int_array(unique_string)

        mkey_bits=utils.int_list_to_bit_list(mkey)

        rkeys=cipher.key_expansion(mkey)

        rkeys_bits = utils.convert_to_2d_bit_list(rkeys)

        # Define empty list to store result
        result = [[0]*(round_key_size*8)]*round_key


        # for each bit in mk
        for i in range(0,mkey_size*8):
            
            

            mkey_bits=utils.int_list_to_bit_list(mkey)

            # change value of bit
            mkey_bits[i] = mkey_bits[i]^1
            # Compute new mk and rk
            new_mkey = utils.bit_list_to_int_list(mkey_bits)
            new_rkeys=cipher.key_expansion(new_mkey)
            new_rkeys_bits = utils.convert_to_2d_bit_list(new_rkeys)
            # xor new and old rk to find different bits
            fark=utils.xor_2d_lists(rkeys_bits,new_rkeys_bits)
            # accumilate different bits
            result=utils.sum_2d_lists(result,fark)


    print(result)

    