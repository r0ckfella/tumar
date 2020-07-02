#!/bin/bash

# start django in production env
export CURRENT_UID=$(id -u)
python ./manage.py collectstatic --noinput &&
python ./manage.py migrate &&
python ./manage.py compilemessages &&
uwsgi --ini ./config/uwsgi.ini --uid ${CURRENT_UID}

# if [ ${PRODUCTION} == "false" ]; then
#     # use development server
# else
#     # use production server
# fi