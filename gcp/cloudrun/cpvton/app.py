import os
from flask import Flask, escape, request, jsonify
from flask_cors import CORS
import subprocess
from subprocess import Popen, PIPE
from flask import escape
import traceback
import pathlib
import shutil
import base64
import cv2
from google.cloud import logging
from google.cloud.logging.resource import Resource

###################
# logging setup
###################
logger = None
try:
    log_client = logging.Client()
    log_name = 'run.googleapis.com%2Frequests'
    #  res = Resource(type="cloud_run",
    #          labels={ "project_id": "virtual-tryon/lip_jppnet" })
    logger = log_client.logger(log_name)
except Exception as error:
    print(error)
    print('probably google cloud logging Could not automatically determine credentials.')
    print('only print to stdout now')

def log(msg, severity='DEBUG'):
    #  logger.log_text(msg)
    #  logger.log_struct({'severity': severity, 'message': msg})
    #  logger.log_text(msg, severity=severity)
    if logger is not None:
        logger.log_struct({"message": msg}, severity=severity)
    else:
        print('[{}] {}'.format(severity, msg))
# end: logging setup


def convert_mask():
    log('converting mask')
    img = cv2.imread('/tmp/cpvton/data/test/cloth-mask/cloth.jpg', cv2.IMREAD_UNCHANGED)

    try:
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        log('writing converted mask')
        cv2.imwrite('/tmp/cpvton/data/test/cloth-mask/cloth.jpg', gray_image)
    except Exception as error:
        log('error while conver_mask, probably already single-channel: {}'.format(error), 'ERROR')


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def openpose():
    #  target = os.environ.get('TARGET', 'World')
    #  return 'Hello {}!\n'.format(target)

    try:
        # mkdir -p
        log('mkdir -p')
        pathlib.Path("/tmp/cpvton/data/test/image").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/cpvton/data/test/image-parse").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/cpvton/data/test/cloth").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/cpvton/data/test/cloth-mask").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/cpvton/data/test/pose").mkdir(parents=True, exist_ok=True)

        # receive file from POST request
        #  file = request.files['file']
        #  filename = secure_filename(file.filename)
        log('saving user POSTed file to /tmp')
        request.files['model'].save(os.path.join('/tmp/cpvton/data/test/image', 'model.jpg'))
        request.files['model-parse'].save(os.path.join('/tmp/cpvton/data/test/image-parse', 'model.png'))
        request.files['cloth'].save(os.path.join('/tmp/cpvton/data/test/cloth', 'cloth.jpg'))
        request.files['cloth-mask'].save(os.path.join('/tmp/cpvton/data/test/cloth-mask', 'cloth.jpg'))
        request.files['pose'].save(os.path.join('/tmp/cpvton/data/test/pose', 'model_keypoints.json'))

        # convert mask to 1 channel jpg
        convert_mask()


        ###############
        # execute pipeline
        ###############
        log("calling run-cpvton.sh")
        p = Popen('/app/run-cpvton.sh', stdout=PIPE, stderr=PIPE,
                cwd='/app')
        stdout, stderr = p.communicate()
        log("done calling run script")
        log("stdout:\n{}".format(str(stdout).replace('\\n', '\n')))
        log("stderr:\n{}".format(str(stderr).replace('\\n', '\n')))
        if p.returncode != 0:
            raise Exception(stderr)

        with open('/tmp/cpvton/result/gmm_final.pth/test/warp-cloth/cloth.jpg', 'rb') as img_file:
            warp_cloth_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        with open('/tmp/cpvton/result/gmm_final.pth/test/warp-mask/cloth.jpg', 'rb') as img_file:
            warp_mask_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        with open('/tmp/cpvton/result/tom_final.pth/test/try-on/model.jpg', 'rb') as img_file:
            tryon_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        return jsonify({
            'warp-cloth': warp_cloth_base64,
            'warp-mask': warp_mask_base64,
            'tryon': tryon_base64
        })

    except Exception as error:
        log('uncaught error: {}'.format(error), 'ERROR')
        trace = traceback.print_exc()
        log(trace, 'ERROR')
        return jsonify({
            'error': str(error),
            'trace': str(trace)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

