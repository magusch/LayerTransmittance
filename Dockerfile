FROM python:3.9-alpine
RUN apk add g++ jpeg-dev zlib-dev libjpeg make
RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN apk add --no-cache --update-cache gfortran build-base wget libpng-dev openblas-dev
RUN apk add --no-cache --update \
    gcc gfortran musl-dev \
    musl-dev linux-headers g++
RUN apk add --update --no-cache py3-numpy
RUN pip install matplotlib
RUN pip install pandas
RUN apk add py3-scipy
RUN pip install scipy==1.8.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /layer_transmittance
ADD . /layer_transmittance
RUN pip install -r requirements.txt