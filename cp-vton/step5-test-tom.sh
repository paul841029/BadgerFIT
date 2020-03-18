#!/usr/bin/env bash
set -ex

NICKNAME=step5-test-tom

TRAIN_LOG_FILENAME="train_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log
VAL_LOG_FILENAME="val_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log

# raw
#python test.py --name tom_test_new --stage TOM --workers 4 --datamode test --data_list test_pairs.txt --checkpoint checkpoints/tom_train_new/tom_final.pth

python3 test.py --name tom_test_new --stage TOM --workers 0 \
               --datamode test --data_list test_pairs.txt \
               --checkpoint checkpoints/tom_train_new/tom_final.pth \
               --gpu_ids 0 | tee ${VAL_LOG_FILENAME}

# RuntimeError: DataLoader worker (pid 2226) is killed by signal: Bus error.
# --workers 4 --> --workers 0

echo "Train... Done."