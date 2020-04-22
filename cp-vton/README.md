
## 0. Download data &  Pretrain model

```
python3 data_download.py # download original train & test data
```

download gmm & tom pretrain model from: 
https://drive.google.com/open?id=18ncLRuKLFtGKabaco9Bur1wCTVQjvAI1

create directory `checkpoints/gmm_train_new/` & `checkpoints/tom_train_new/` <br>
place `gmm_final.pth` into `checkpoints/gmm_train_new/` <br>
place `tom_final.pth` into `checkpoints/tom_train_new/`

## 1. Train

```
sh step1-train-gmm.sh # no need this step since we use pretrain model
sh step2-test-gmm.sh
sh step3-generate-tom-data.sh
mv result/gmm_final.pth/train/* data/train/
mv result/gmm_final.pth/test/warp-mask data/test/
mv result/gmm_final.pth/test/warp-cloth data/test/
sh step4-train-tom.sh # no need this step since we use pretrain model
sh step5-test-tom.sh
```

**TensorBoard**

```
tensorboard/
├── gmm_traintest_new
│   └── events.out.tfevents.1568185067.tplustf-imagealgo-50529-ever-chief-0
├── tom_test_new
│   └── events.out.tfevents.1568473618.tplustf-imagealgo-50529-ever-chief-0
    
$ tensorboard --logdir tensorboard/gmm_traintest_new/
$ tensorboard --logdir tensorboard/tom_test_new/
```

web: 

	http://everdemacbook-pro.local:6006/#scalars
	http://everdemacbook-pro.local:6006/#images

scalars / images :

	gmm_traintest_new

![](pics/gmm-traintest-images.png)

	tom_test_new

![](pics/tom-test.png)


## 2. Visualize
Run ```python smart_show_test_result.py```. Can see result image in ```result_simple``` <br>
The image information from left to right is
[cloth, cloth-mask, model-image, model-image-parse, cloth-warp, cloth-warp-mask, try-on-result]
![](pics/src_012578_dst_014252.png)
![](pics/src_012849_dst_015439.png)
![](pics/src_012934_dst_010551.png)
![](pics/src_013355_dst_018626.png)
![](pics/src_013583_dst_006296.png)
![](pics/src_013725_dst_005920.png)
![](pics/src_017823_dst_007923.png)
![](pics/src_018876_dst_000192.png)
![](pics/src_019531_dst_015077.png)


## 4. Virtual Try-On Technique bottleneck

**Striped clothes**
![](pics/src_012377_dst_017227_p1.png)
![](pics/src_019001_dst_010473_p1.png)
![](pics/src_013309_dst_002031_p1.png)

**Arm hover clothes**
![](pics/src_012830_dst_008479_p2.png)
![](pics/src_012975_dst_007423_p2.png)
 
