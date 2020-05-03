import subprocess
from subprocess import Popen, PIPE
from subprocess import check_output
from flask import escape
from google.cloud import storage
import zipfile
import os
from google.cloud import logging
from google.cloud.logging.resource import Resource
from distutils.dir_util import copy_tree
import pathlib
import traceback

# We keep model as global variable so we don't have to reload it in case of warm invocations
model = None

###################
# logging setup
###################
log_client = logging.Client()
# This is the resource type of the log
log_name = 'cloudfunctions.googleapis.com%2Fcloud-functions'

# Inside the resource, nest the required labels specific to the resource type
res = Resource(type="cloud_function",
        labels={ "function_name": os.getenv('FUNCTION_NAME'), "region": os.getenv('FUNCTION_REGION') })
logger = log_client.logger(log_name)
def log(msg, severity='DEBUG'):
    logger.log_struct({"message": msg}, resource=res, severity=severity)
# end: logging setup

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    log('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))

# main function
def cpvton_pipeline(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    #  request_json = request.get_json(silent=True)
    #  request_args = request.args

    #  if request_json and 'name' in request_json:
    #      name = request_json['name']
    #  elif request_args and 'name' in request_args:
    #      name = request_args['name']
    #  else:
    #      name = 'World'
    #  return 'Hello {}!'.format(escape(name))


    try:
        ###############
        # Download model for LIP_JPPNet
        ###############
        global model

        log("model={}".format(model))
        # Model load which only happens during cold starts
        #  if model is None:
        if not os.path.isdir('/tmp/tryon'):
            pathlib.Path("/tmp/tryon").mkdir(parents=True, exist_ok=True)
            # copy
            log("copying folder")
            copy_tree(".", "/tmp/tryon")

            # download models
            log("downloading gmm")
            download_blob('virtual-tryon.appspot.com', 'cp-vton/gmm_final.pth', '/tmp/tryon/cp-vton/checkpoints/gmm_train_new/gmm_final.pth')
            log("downloading tom")
            download_blob('virtual-tryon.appspot.com', 'cp-vton/tom_final.pth', '/tmp/tryon/cp-vton/checkpoints/tom_train_new/tom_final.pth')
            log("downloading JPPNet")
            download_blob('virtual-tryon.appspot.com', 'JPPNet-s2.zip', '/tmp/JPPNet-s2.zip')

            log("unzip model")
            with zipfile.ZipFile('/tmp/JPPNet-s2.zip', 'r') as zip_ref:
                zip_ref.extractall('/tmp/tryon/LIP_JPPNet/checkpoint')
            model = True


        ###############
        # execute pipeline
        ###############
        log("calling script")
        p = Popen('/tmp/tryon/pipeline.sh', stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        return """
            <h2>stdout:</h2>
            <pre>{}</pre>
            <h2>stderr:</h2>
            <pre>{}</pre>
        """.format(escape(stdout), escape(stderr))

    except Exception as error:
        log('uncaught error: {}'.format(error), 'ERROR')
        log(traceback.print_exc(), 'ERROR')
        return """
            <h2>Exception:</h2>
            <pre>{}</pre>
        """.format(escape(traceback.print_exc()))

