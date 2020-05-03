# Cloud Run Dockerized Openpose-as-a-Service

## Build image

```bash
docker build -t "virtual-tryon/openpose"
```

## Test locally

```bash
# run server
docker run -it -p 8080:8080 -e PORT=8080 virtual-tryon/openpose

# test client
python3 client.py --host=localhost:8080
# the keypoints json will be printed, and the rendered image will be saved to rendered.png
```

## Deploy to GCP

First login and select project with gcloud CLI

### Build in gcr.io (Google Container Registry)

```bash
gcloud builds submit --config cloudbuild.yaml .
```

### Deploy to Cloud Run

```bash
gcloud run deploy --image gcr.io/virtual-tryon/openpose --platform managed --memory 2048
```

