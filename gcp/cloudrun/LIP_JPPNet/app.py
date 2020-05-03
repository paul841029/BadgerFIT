import os
from flask import Flask, escape, request, jsonify
import subprocess
from subprocess import Popen, PIPE
from flask import escape
import traceback
import pathlib
import shutil
import base64
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



app = Flask(__name__)

@app.route('/', methods=['POST'])
def openpose():
    #  target = os.environ.get('TARGET', 'World')
    #  return 'Hello {}!\n'.format(target)

    try:
        # mkdir -p
        log('mkdir -p')
        pathlib.Path("/tmp/input/images").mkdir(parents=True, exist_ok=True)
        pathlib.Path("/tmp/output").mkdir(parents=True, exist_ok=True)

        # receive file from POST request
        file = request.files['file']
        #  filename = secure_filename(file.filename)
        log('saving user POSTed file to /tmp')
        file.save(os.path.join('/tmp/input/images', 'user.jpg'))

        # testing only
        #  shutil.copy(str(pathlib.Path('/app/c_resized.jpg')), str(pathlib.Path('/tmp/img_input/c_resized.jpg')))


        ###############
        # execute pipeline
        ###############
        log("calling run-lip_jppnet.sh")
        p = Popen('/app/run-lip_jppnet.sh', stdout=PIPE, stderr=PIPE,
                cwd='/app')
        stdout, stderr = p.communicate()
        log("done calling run script")
        log("stdout:\n{}".format(str(stdout).replace('\\n', '\n')))
        log("stderr:\n{}".format(str(stderr).replace('\\n', '\n')))

        with open('/tmp/output/user.png', 'rb') as img_file:
            output_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        with open('/tmp/output/user_vis.png', 'rb') as img_file:
            vis_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        return jsonify({
            'output': output_base64,
            'vis': vis_base64
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

