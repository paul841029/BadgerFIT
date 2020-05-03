#!/bin/bash

set -ex

gcloud builds submit --config cloudbuild.yaml .

gcloud run deploy lip_jppnet --image gcr.io/virtual-tryon/lip_jppnet --platform managed --region us-central1 --memory 2048

notify-send "Done building and deploying lip_jppnet to cloudrun"
