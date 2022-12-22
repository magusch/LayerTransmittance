FROM python:3.9-alpine
RUN apk add g++ jpeg-dev zlib-dev libjpeg make
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade pip setuptools wheel
RUN apk add --no-cache --update-cache gfortran build-base wget libpng-dev openblas-dev
RUN apk add --no-cache --update \
    gcc gfortran musl-dev \
    musl-dev linux-headers g++
RUN apk add --update --no-cache py3-numpy
RUN apk add py3-scipy
RUN pip3 install --extra-index-url https://alpine-wheels.github.io/index numpy==1.23.5
RUN pip3 install --extra-index-url https://alpine-wheels.github.io/index pandas==1.5.2
RUN pip3 install --extra-index-url https://alpine-wheels.github.io/index scipy
RUN pip3 install matplotlib==3.6.2
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /layer_transmittance
ADD . /layer_transmittance
RUN pip3 install -r requirements.txt