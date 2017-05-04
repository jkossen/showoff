FROM alpine:latest
RUN apk update
RUN apk add bash git python py-pip python-dev \
    build-base jpeg-dev zlib-dev musl-dev libjpeg openjpeg
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

