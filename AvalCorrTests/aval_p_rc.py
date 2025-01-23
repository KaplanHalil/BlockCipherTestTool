"""
p-rc Aval Test

Rasgele 1000 adet p alir ve her bir bitini tek tek değiştirip round ciktilarini hesaplar.
Genel beklenti rc'daki her bit bitin 450-550 arasinda değişmesidir.
Buna göre convert_2d_list fonksiyonunda 255 beyaz 0 siyah olacak şekilde piksellere renk atar.
Çikti olarak verdiği resimde sol taraf p bitleri üst raraf rc bitleri.


"""

from PIL import Image
import utils
import Alg as cipher
import time


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

if __name__ == "__main__":

    a = time.time()
    # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
    img = Image.new( 'L', (cipher.ciphertext_size*8*cipher.num_rounds,cipher.plaintext_size*8), "black") # create a new black image
    pixels = img.load() # create the pixel map

    # for each bit in plaintext
    for i in range(0,cipher.plaintext_size*8):
    
        # Define empty list to store result
        result = [[0 for _ in range(cipher.ciphertext_size * 8)] for _ in range(cipher.num_rounds)]
        # Generate 1000 unique plaintexts
        for k in range(1000):
        
            # Convert the counter `k` to a hexadecimal string with zero-padding
            hex_value = ''.join(f"{(k + j) % 256:02x}" for j in range(cipher.plaintext_size))
            unique_p = f"0x{hex_value}"
    
            plaintext = utils.str_to_int_array(unique_p)

            plaintext_bits=utils.int_list_to_bit_list(plaintext)

            mkey= [0]*cipher.mkey_size

            ciphertext=cipher.return_rc(plaintext,mkey) # round ciphertexts

            ciphertext_bits = utils.convert_to_2d_bit_list(ciphertext)

            # change value of bit
            plaintext_bits[i] = plaintext_bits[i]^1

            new_plaintext = utils.bit_list_to_int_list(plaintext_bits)

            # Compute new rc
            new_ciphertext=cipher.return_rc(new_plaintext,mkey)

            new_ciphertext_bits = utils.convert_to_2d_bit_list(new_ciphertext)
            # xor new and old rc to find different bits
            fark=utils.xor_2d_lists(ciphertext_bits,new_ciphertext_bits)
            # accumilate different bits
            result=utils.sum_2d_lists(result,fark)

        
        draw_list = convert_2d_list(result)
        
        for j in range(img.size[0]):    # For every row
               pixels[j,i] = (draw_list[j]) # set the colour accordingly
        

    img.save("aval_p-rc.png")
    b=time.time()
    print("Time of aval_p-rc: ",(b-a)/60,"minutes")



    