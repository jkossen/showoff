FROM python:2.7-slim

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update \
    && apt-get -yq install \
    build-essential \
    git-core \
    libffi-dev \
    libyaml-dev \
    libjpeg-dev \
    zlib1g-dev \ 
    libssl-dev \
    python-setuptools
ENV LIBRARY_PATH=/lib:/usr/lib
ENV SECRET_KEY=AJI2RhfhJGcg1Jb9zXLyEYqdQvjx3QBU2GJ7pyYRMsLAfI7M2d8rNpY 
ENV GALLERY_TITLE="photo gallery"
#override this by setting -e
RUN mkdir -p /var/lib/showoff/cache
RUN mkdir -p /var/lib/showoff/shows
RUN mkdir -p /var/lib/showoff/edits
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app
RUN python setup.py install

