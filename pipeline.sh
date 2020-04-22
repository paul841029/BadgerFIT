#!/usr/bin/env bash
set -ex

# TODO:
# 1. crop and resize image, cloth, cloth-mask to 256x192
# 2. combine with Paul's openpose
# 3. combine with Dax's background removal to generate mask

# input image model & cloth & cloth-mask
INPUT_IMAGE_PATH=./example/image/a_0.jpg
INPUT_IMAGE_POSE_PATH=./example/image/a_0_keypoints.json
INPUT_IMAGE_CLOTH_PATH=./example/cloth/003514_1.jpg
INPUT_IMAGE_CLOTH_MASK_PATH=./example/cloth-mask/003514_1.jpg
FILENAME="$(basename $INPUT_IMAGE_PATH)"
CLOTH_FILENAME="$(basename $INPUT_IMAGE_CLOTH_PATH)"

# LIP_JPPNet variable
PARSE_OUTPUT_DIR=./LIP_JPPNet/output/parsing/val
file=somefile.whatevs
PNG_FILENAME="${FILENAME%.*}.png"
IMAGE_MODEL_PARSE_PATH=$PARSE_OUTPUT_DIR/$PNG_FILENAME

# cp-vton variable
CPVTON_DATA_DIR=./cp-vton/data/test
CPVTON_CLOTH_DIR=$CPVTON_DATA_DIR/cloth
CPVTON_CLOTH_WARP_DIR=$CPVTON_DATA_DIR/warp-cloth
CPVTON_CLOTH_MASK_DIR=$CPVTON_DATA_DIR/cloth-mask
CPVTON_CLOTH_WARP_MASK_DIR=$CPVTON_DATA_DIR/warp-mask
CPVTON_IMAGE_DIR=$CPVTON_DATA_DIR/image
CPVTON_IMAGE_PARSE_DIR=$CPVTON_DATA_DIR/image-parse
CPVTON_IMAGE_POSE_DIR=$CPVTON_DATA_DIR/pose

# step1. generate parse image
cd LIP_JPPNet
python single_parsing.py --image_path ../$INPUT_IMAGE_PATH
echo $IMAGE_MODEL_PARSE_PATH
cd ..

cp $IMAGE_MODEL_PARSE_PATH $CPVTON_IMAGE_PARSE_DIR
# step2. generate image pose keypoint
# using Openpose...
# now we assume image's pose is already placed in $CPVTON_IMAGE_POSE_DIR

# step3. generate warp cloth & mask using GMM
cp $INPUT_IMAGE_PATH $CPVTON_IMAGE_DIR
cp $INPUT_IMAGE_CLOTH_PATH $CPVTON_CLOTH_DIR
cp $INPUT_IMAGE_CLOTH_MASK_PATH $CPVTON_CLOTH_MASK_DIR
cp $INPUT_IMAGE_POSE_PATH $CPVTON_IMAGE_POSE_DIR

cd cp-vton
python3 generate_custom_pairs.py $FILENAME $CLOTH_FILENAME
python3 test.py --name gmm_traintest_new \
                --stage GMM --workers 0 --datamode test \
                --data_list custom_pairs.txt \
                --checkpoint checkpoints/gmm_train_new/gmm_final.pth

# step4. generate final try-on image using TOM
python3 test.py --name tom_test_new --stage TOM --workers 0 \
                --datamode test --data_list custom_pairs.txt \
                --checkpoint checkpoints/tom_train_new/tom_final.pth
cd ..

# step5. mv result to example dir
# result is stored at ./cp-vton/result/tom_final.pth/test/try-on/
CPVTON_OUTPUT_DIR=./cp-vton/result/tom_final.pth/test/try-on/
OUTPUT_DIR=./example/try-on-result/
cp $CPVTON_OUTPUT_DIR$FILENAME $OUTPUT_DIR
