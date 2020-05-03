#!/bin/bash

set -ex

gcloud builds submit --config cloudbuild.yaml .

gcloud run deploy lip-jppnet --image gcr.io/virtual-tryon/lip_jppnet --platform managed --region us-central1 --memory 2048

if command -v notify-send 2>/dev/null; then
  notify-send "Done building and deploying lip-jppnet to cloudrun"
fi

