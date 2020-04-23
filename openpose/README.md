* Build image
```bash
sudo docker build . -f Dockerfile.cpuonly -t "seancook/openpose-cpu"
```

* Run container (assuming input images are in `pwd`)
```bash
docker run -v`pwd`:/data -it seancook/openpose-cpu -display 0 -image_dir /data -write_images /data --model_pose COCO --write_json /data
```
