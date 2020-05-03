FROM ubuntu:18.04

# LABEL maintainer="sean@seancook.dev"
# LABEL description="CPU-only version of OpenPose. Not slimmed for production."
# LABEL version="1.0"

ENV DEBIAN_FRONTEND=noninteractive

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
# COPY . ./

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y wget apt-utils lsb-core cmake git libopencv-dev
# install python3.7
RUN apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.7 python3-pip && \
    python3.7 --version && \
    cd /usr/local/bin && \
    ln -svf /usr/bin/python3.7 python3 && \
    ln -svf /usr/bin/python3.7 python && \
    python3.7 --version && \
    python3 --version && \
    python --version && \
    pip3 install --upgrade pip

#########
# build openpose from source
#########
RUN git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git

WORKDIR openpose
RUN git checkout caa794cf81bed53b9e114299b715a6d972097b5b

WORKDIR scripts/ubuntu

RUN sed -i 's/\<sudo -H\>//g' install_deps.sh; \
   sed -i 's/\<sudo\>//g' install_deps.sh; \
   sed -i 's/\<easy_install pip\>//g' install_deps.sh; \
   sync; sleep 1; bash install_deps.sh

WORKDIR /app/openpose/build

# pre-trained models, put this before cmake do avoid downloading from flacky CMU server
COPY pose_iter_584000.caffemodel /app/openpose/models/pose/body_25/
COPY pose_iter_440000.caffemodel /app/openpose/models/pose/coco/

RUN cmake -DGPU_MODE:String=CPU_ONLY \
          -DDOWNLOAD_BODY_MPI_MODEL:Bool=OFF \
          -DDOWNLOAD_BODY_COCO_MODEL:Bool=OFF \
          -DDOWNLOAD_FACE_MODEL:Bool=OFF \
          -DDOWNLOAD_HAND_MODEL:Bool=OFF \
          -DUSE_MKL:Bool=OFF \
          ..

RUN make

RUN apt-get remove wget unzip cmake git build-essential -y && apt-get autoremove -y
# end: build openpose from source


# Install production dependencies.
WORKDIR $APP_HOME
COPY requirements.txt .
RUN pip3 install --quiet -r requirements.txt

# copy source
# COPY c_resized.jpg .
COPY run-openpose.sh .
COPY postprocess.py .
COPY app.py .

# ENTRYPOINT ["build/examples/openpose/openpose.bin"]
#
# CMD ["--help"]

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

