#!/usr/bin/env bash
set -ex

NICKNAME=step4-train-tom

TRAIN_LOG_FILENAME="train_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log
VAL_LOG_FILENAME="val_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log

# raw
#python train.py --name gmm_train_new --stage GMM --workers 4 --save_count 5000 --shuffle

python3 train.py --name tom_train_new --stage TOM --workers 0 --save_count 5000 --shuffle \
                   --gpu_ids 0 | tee ${TRAIN_LOG_FILENAME}

# RuntimeError: DataLoader worker (pid 2226) is killed by signal: Bus error.
# --workers 4 --> --workers 0

echo "Train... Done."