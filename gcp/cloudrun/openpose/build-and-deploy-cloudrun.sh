#!/bin/bash

set -ex

gcloud builds submit --config cloudbuild.yaml .

gcloud run deploy openpose --image gcr.io/virtual-tryon/openpose --platform managed --region us-central1 --memory 2048

notify-send "Done building and deploying openpose to cloudrun"
