FROM python:3.6

WORKDIR /usr/src/app

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
      apt-transport-https && \
    rm -rf /var/lib/apt/lists/*


RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && /usr/sbin/locale-gen

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . code

COPY celerybeat /etc/default/celerybeat
COPY celerybeat-init /etc/init.d/celerybeat
COPY celeryd /etc/default/celeryd
COPY celeryd-init /etc/init.d/celeryd
RUN chmod +x /etc/init.d/celeryd /etc/init.d/celerybeat && chmod 640 '/etc/default/celerybeat' '/etc/default/celeryd'

WORKDIR code

EXPOSE 8088

RUN adduser --disabled-password --gecos '' celery && usermod -a -G root celery && chmod 770 '/usr/src/app/code/'