import os
from flask import Flask, escape, request, jsonify
import subprocess
from subprocess import Popen, PIPE
from flask import escape
import traceback
import pathlib
import shutil
import base64
import json
#  from google.cloud import logging
#  from google.cloud.logging.resource import Resource

###################
# logging setup
###################
#  log_client = logging.Client()
#  log_client.setup_logging()
#  logger = log_client.logger('my-log')
def log(msg, severity='DEBUG'):
    print('[{}] {}'.format(severity, msg))
    #  logger.log_text(msg)
    #  logger.log_struct({'severity': severity, 'message': msg})
    #  logger.log_text(msg, severity=severity)
# end: logging setup


def post_process(s):
    obj = json.loads(s)
    people = obj['people']
    for idx, _ in enumerate(people):
        kp = people[idx]['pose_keypoints_2d']
        people[idx] = {}
        people[idx]['pose_keypoints'] = kp

    return json.dumps(obj, indent=2)
        


app = Flask(__name__)

@app.route('/', methods=['POST'])
def openpose():
    #  target = os.environ.get('TARGET', 'World')
    #  return 'Hello {}!\n'.format(target)

    try:
        # mkdir -p
        log('mkdir -p')
        pathlib.Path("/tmp/img_input").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/rendered").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/kp").mkdir(parents=True, exist_ok=True)

        # receive file from POST request
        file = request.files['file']
        #  filename = secure_filename(file.filename)
        log('saving user POSTed file to /tmp')
        file.save(os.path.join('/tmp/img_input', 'user.jpg'))

        # testing only
        #  shutil.copy(str(pathlib.Path('/app/c_resized.jpg')), str(pathlib.Path('/tmp/img_input/c_resized.jpg')))


        ###############
        # execute pipeline
        ###############
        log("calling openpose.bin")
        p = Popen('/app/run-openpose.sh', stdout=PIPE, stderr=PIPE,
                cwd='/app/openpose')
        stdout, stderr = p.communicate()
        log("done calling openpose.bin")
        log("openpose stdout:\n{}".format(str(stdout).replace('\\n', '\n')))
        log("openpose stderr:\n{}".format(str(stderr).replace('\\n', '\n')))

        with open('/tmp/kp/user_keypoints.json', 'r') as kp_file:
            kp = kp_file.read()
        with open('/tmp/rendered/user_rendered.png', 'rb') as img_file:
            rendered_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        # post process keypoints
        kp = post_process(kp)

        return jsonify({
            'keypoints': kp,
            'rendered': rendered_base64
        })

    except Exception as error:
        log('uncaught error: {}'.format(error), 'ERROR')
        trace = traceback.print_exc()
        log(trace, 'ERROR')
        return jsonify({
            'error': error,
            'trace': trace
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

