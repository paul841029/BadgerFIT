import sys

model_img = sys.argv[1]
cloth_img = sys.argv[2]
f = open("./data/custom_pairs.txt", "w")
f.truncate(0)
f.write(model_img + " " + cloth_img)
f.close()