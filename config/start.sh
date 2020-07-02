#!/bin/bash

# start django in production env
python ./manage.py collectstatic --noinput &&
python ./manage.py migrate &&
python ./manage.py compilemessages &&
uwsgi --ini ./config/uwsgi.ini --uid 1000

# if [ ${PRODUCTION} == "false" ]; then
#     # use development server
# else
#     # use production server
# fi