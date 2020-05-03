import argparse
import requests
import base64
import json

CLOUD_RUN_URL = 'https://openpose-s3mg3fuleq-uc.a.run.app'

parser = argparse.ArgumentParser()
parser.add_argument("--host", default=CLOUD_RUN_URL, help="the host of server, eg. localhost:8080 defaults to cloud run url")
args = parser.parse_args()

url = 'http://{}'.format(args.host)

img = open('a_0.jpg', 'rb')

content_type = 'image/jpeg'
files={'file': ('user.jpg', img, content_type)}

#  url = 'http://localhost:8080/'

############
# call API
############
response = requests.post(url, files=files)
print("got response!\n")
if response.status_code == 200:
    parsed = response.json()

    with open("output.png", "wb") as fh:
        fh.write(base64.decodebytes(parsed['output'].encode()))
    print("\noutput image saved to output.png")
    with open("vis.png", "wb") as fh:
        fh.write(base64.decodebytes(parsed['vis'].encode()))
    print("\nvis image saved to vis.png")

else:
    print(response.text)

