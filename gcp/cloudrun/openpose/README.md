# Cloud Run Dockerized Openpose-as-a-Service

## Prepare

First you need to Download pre-trained model. Put the two files in the current directory

```
https://drive.google.com/drive/folders/15SXpfJ5L1W7rzTIiFpEu2zza-Dt27vsX?usp=sharing
```

## Develop Locally

### Build image

```bash
docker build -t virtual-tryon/openpose
```


### Test locally

```bash
# run server
docker run -it -p 8080:8080 -e PORT=8080 virtual-tryon/openpose

# test client
python3 client.py --host=localhost:8080
# the keypoints json will be printed, and the rendered image will be saved to rendered.png
```


## Deploy to GCP

First login and select project with gcloud CLI


### Build in gcr.io (Google Container Registry) and Deploy to Cloud Run

```bash
./build-and-deploy-cloudrun.sh
```

