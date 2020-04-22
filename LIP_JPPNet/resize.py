import cv2
import glob
from PIL import Image
 
filenames = [img for img in glob.glob("datasets/examples/images/*.jpg")]

filenames.sort() # ADD THIS LINE

images = []
for img in filenames:
    print(img)
    src = cv2.imread(img, cv2.IMREAD_UNCHANGED)
    src = src[0:2000, 250:1750] # this is for uniqlo
    print(src.shape)
    # dsize
    dsize = (192, 256)

    # resize image
    output = cv2.resize(src, dsize)
    cv2.imwrite(img[:-4] + '_resized.jpg',output) 

