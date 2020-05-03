import argparse
import requests
import base64
import json

CLOUD_RUN_URL = 'https://openpose-s3mg3fuleq-uc.a.run.app'

parser = argparse.ArgumentParser()
parser.add_argument("--host", default=CLOUD_RUN_URL, help="the host of server, eg. localhost:8080 defaults to cloud run url")
args = parser.parse_args()

url = 'http://{}'.format(args.host)

img = open('c_resized.jpg', 'rb')

content_type = 'image/jpeg'
files={'file': ('user.jpg', img, content_type)}

#  url = 'http://localhost:8080/'

############
# call API
############
response = requests.post(url, files=files)
print("got response!\n")

parsed = response.json()
print("keypoints: \n{}".format(json.dumps(json.loads(parsed['keypoints']), indent=2)))

with open("rendered.png", "wb") as fh:
    fh.write(base64.decodebytes(parsed['rendered'].encode()))
print("\nrendered image saved to rendered.png")

