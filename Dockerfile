FROM python:3.9-alpine
RUN apk add g++ jpeg-dev zlib-dev libjpeg make
RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN apk add --no-cache --update-cache gfortran build-base wget libpng-dev openblas-dev
RUN apk add --no-cache --update \
    gcc gfortran musl-dev \
    musl-dev linux-headers g++
RUN apk add --update --no-cache py3-numpy
RUN apk add py3-scipy
RUN pip install numpy==1.23.5
RUN pip install pandas==1.5.2
RUN pip install scipy==1.8.0
RUN pip install matplotlib==3.6.2
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /layer_transmittance
ADD . /layer_transmittance
RUN pip install -r requirements.txt