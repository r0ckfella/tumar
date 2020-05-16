FROM python:3.6

WORKDIR /code

RUN apt-get update -y && \
  apt-get install --auto-remove -y \
  libgeos-dev \
  binutils \
  libproj-dev \
  gdal-bin \
  libgdal-dev \
  python3-gdal \
  curl \
  mc \
  nano\
  locales \
  gettext \
  postgresql \
  apt-transport-https \
  build-essential && \
  rm -rf /var/lib/apt/lists/*


RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && /usr/sbin/locale-gen

# Allows docker to cache installed dependencies between builds
COPY ./requirements/ ./requirements/
RUN pip install -r ./requirements/prod.txt

# Adds our application code to the image
COPY . .

EXPOSE 8088

RUN mkdir /imgback_rasters /static