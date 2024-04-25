FROM python:3.9-slim-buster
RUN apt-get update
RUN apt-get install -y g++ zlib1g-dev libjpeg-dev make
RUN pip install --upgrade pip
RUN pip install numpy==1.23.5
RUN pip install pandas==1.5.2
RUN pip install scipy==1.8.0
RUN apt-get install -y \
    gcc gfortran musl-dev
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /layer_transmittance
ADD . /layer_transmittance
RUN pip install -r requirements.txt