FROM ubuntu:trusty

# Define Python required libraries in requirements.txt
# Copy requirements file into the Docker image
COPY requirements.txt /tmp/requirements.txt

# Install required software via apt and pip
RUN sudo apt-get -y update && \
	apt-get install -y \
    awscli \
    python \
    python-pip \
    software-properties-common \
 && add-apt-repository ppa:ubuntugis/ppa \
 && apt-get -y update \
 && apt-get install -y \
 	gdal-bin \
 && pip install --requirement /tmp/requirements.txt

# Copy Build Thumbnail script to Docker image and add execute permissions
COPY build-thumbnails.py build-thumbnails.py

RUN chmod +x build-thumbnails.py
  