* Build image
```bash
sudo docker build . -f Dockerfile.cpuonly -t "seancook/openpose-cpu"
```

* Make directory
```bash
mkdir -p kp
mkdir -p rendered
```
* Download pre-trained model. Extra the two files to the current directory
  ```
  https://drive.google.com/drive/folders/15SXpfJ5L1W7rzTIiFpEu2zza-Dt27vsX?usp=sharing
  ```


* Run container (assuming input images are in `pwd`)
```bash
docker run -v`pwd`:/data --user $(id -u):$(id -g) \
-it seancook/openpose-cpu \
-display 0 -image_dir /data \
-write_images /data/rendered \
--model_pose COCO \
--write_json /data/kp
```

* Postprocess keypoints
```bash
python3 postprcoess.py kp3
```
