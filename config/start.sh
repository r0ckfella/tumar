#!/bin/bash

# start django in production env
python ./manage.py collectstatic --noinput &&
python ./manage.py migrate &&
python ./manage.py compilemessages &&
uwsgi --ini ./config/uwsgi.ini

# if [ ${PRODUCTION} == "false" ]; then
#     # use development server
# else
#     # use production server
# fi