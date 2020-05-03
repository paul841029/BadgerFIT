#!/usr/bin/env bash
set -ex

# step1. generate parse image
# func_LIP_JPPNet()
python3 single_parsing.py --image_dir /tmp/input --image_list ./val.txt --output_dir /tmp/output
# cp ./LIP_JPPNet/output/parsing/val/a_0.png $CPVTON_IMAGE_PARSE_DIR

