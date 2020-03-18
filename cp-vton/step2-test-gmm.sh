#!/usr/bin/env bash
set -ex

NICKNAME=step2-test-gmm

TRAIN_LOG_FILENAME="train_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log
VAL_LOG_FILENAME="val_`date +%Y%m%d_%H%M%S`_"${NICKNAME}.log

# raw 
#python test.py --name gmm_traintest_new --stage GMM --workers 4 --datamode test --data_list test_pairs.txt --checkpoint checkpoints/gmm_train_new/gmm_final.pth

python3 -u test.py --name gmm_traintest_new \
                  --stage GMM --workers 0 --datamode test \
                  --data_list test_pairs.txt \
                  --checkpoint checkpoints/gmm_train_new/gmm_final.pth | tee ${VAL_LOG_FILENAME}


# RuntimeError: DataLoader worker (pid 2226) is killed by signal: Bus error.
# --workers 4 --> --workers 0

echo "Train... Done."