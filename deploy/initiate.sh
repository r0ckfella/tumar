#!/bin/bash
set -e

set -a # automatically export all variables
. .env
set +a

### Configuration ###

REMOTE_SCRIPT_PATH=/home/user/projects/tumar-backend/deploy/deploy.sh

# This is sensitive data
# Do not commit the data
# These $ variables should be in the .env file
# ----------------------
USER=$DEPLOY_SSH_USER
IP=$DEPLOY_SSH_IP
# Port is optional
PORT=$DEPLOY_SSH_PORT
# ----------------------

# echo $USER $IP $PORT

### Library ###

function run()
{
  echo "Running: $@"
  "$@"
}


### Automation steps ###

if [[ "$PORT" != "" ]]; then
  ARGS="-p $PORT"
else
  ARGS=
fi

echo "---- Running deployment script on remote server ----"
# After this line you will be prompted with the password
run ssh $USER@$IP $ARGS bash $REMOTE_SCRIPT_PATH