FROM python:3.6
ENV PYTHONUNBUFFERED 1

# Update and install packages recomended by Django documentation:
# https://docs.djangoproject.com/ja/1.9/ref/contrib/gis/install/geolibs/
# and extra needed packages
RUN apt-get update -y && \
    apt-get install --auto-remove -y \
      libgeos-dev \
      binutils \
      libproj-dev \
      gdal-bin \
      libgdal-dev \
      python3-gdal \
      curl \
      locales \
      gettext \
      apt-transport-https && \
    rm -rf /var/lib/apt/lists/*


RUN echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && /usr/sbin/locale-gen

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . code
WORKDIR code

EXPOSE 8000

# Migrates the database, uploads staticfiles, and runs the production server
CMD ./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    newrelic-admin run-program gunicorn --bind 0.0.0.0:$PORT --access-logfile - tumar.wsgi:application
