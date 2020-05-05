FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y software-properties-common libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# pre-trained models
COPY checkpoints ./checkpoints

# code I seldom edit XD
COPY networks.py .

# Install production dependencies.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# copy source
WORKDIR /tmp/cpvton/data
COPY custom_pairs.txt /tmp/cpvton/data
WORKDIR $APP_HOME
COPY cp_dataset.py .
COPY grid.png .
COPY visualization.py .
COPY run-cpvton.sh .
COPY test.py .
COPY app.py .

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

