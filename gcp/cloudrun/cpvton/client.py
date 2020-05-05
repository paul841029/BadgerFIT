import argparse
import requests
import base64
import json

CLOUD_RUN_URL = ''

parser = argparse.ArgumentParser()
parser.add_argument("--host", default=CLOUD_RUN_URL, help="the host of server, eg. localhost:8080 defaults to cloud run url")
args = parser.parse_args()

if args.host.startswith('http'):
    url = args.host
else:
    url = 'http://{}'.format(args.host)

files = [
        ('model', ('model.jpg', open('model.jpg', 'rb'), 'image/jpeg')),
        ('model-parse', ('model-parse.png', open('model-parse.png', 'rb'), 'image/png')),
        ('cloth', ('cloth.jpg', open('cloth.jpg', 'rb'), 'image/jpeg')),
        ('cloth-mask', ('cloth-mask.jpg', open('cloth-mask.jpg', 'rb'), 'image/jpeg')),
        ('pose', ('pose.json', open('pose.json', 'rb'), 'image/jpeg')),
]

#  url = 'http://localhost:8080/'

############
# call API
############
response = requests.post(url, files=files)
print("got response!\n")
if response.status_code == 200:
    parsed = response.json()

    with open("warp-cloth.jpg", "wb") as fh:
        fh.write(base64.decodebytes(parsed['warp-cloth'].encode()))
    print("\nwarp cloth image saved to warp-cloth.jpg")
    with open("warp-mask.jpg", "wb") as fh:
        fh.write(base64.decodebytes(parsed['warp-mask'].encode()))
    print("\nwarp cloth mask image saved to warp-mask.jpg")
    with open("tryon.jpg", "wb") as fh:
        fh.write(base64.decodebytes(parsed['tryon'].encode()))
    print("\ntryon image saved to tryon.jpg")

else:
    print(response.text)

