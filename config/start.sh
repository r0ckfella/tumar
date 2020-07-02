#!/bin/bash

# start django in production env
export CURRENT_UID=$(id -u) CURRENT_GID=$(id -g)
python ./manage.py collectstatic --noinput &&
python ./manage.py migrate &&
python ./manage.py compilemessages &&
uwsgi --ini ./config/uwsgi.ini --uid ${CURRENT_ID} --gid ${CURRENT_GID}

# if [ ${PRODUCTION} == "false" ]; then
#     # use development server
# else
#     # use production server
# fi