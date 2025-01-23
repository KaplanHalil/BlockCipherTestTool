
from PIL import Image

# PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
img = Image.new( 'L', (256*15,256), "black") # create a new black image
pixels = img.load() # create the pixel map

for i in range(img.size[0]):    # for every col:
    for j in range(img.size[1]):    # For every row
        pixels[i,j] = (0) # set the colour accordingly
        pixels[0,0] = (255) # set the colour accordingly
        

img.show()
img.save("deneme.png")