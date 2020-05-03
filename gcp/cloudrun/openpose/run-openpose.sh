#!/bin/bash

set -ex

cd /app/openpose
build/examples/openpose/openpose.bin -display 0 --net_resolution 320x176 -image_dir /tmp/img_input -write_images /tmp/rendered --model_pose COCO --write_json /tmp/kp

