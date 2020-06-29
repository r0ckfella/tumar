#!/bin/bash
set -e

set -a # automatically export all variables
. .env
set +a

### Configuration ###

REMOTE_SCRIPT_PATH=~/projects/tumar-backend/deploy/deploy.sh

# This is sensitive data
# Do not commit the data
# ----------------------
USER=
IP=
# Port is optional
PORT=
# ----------------------


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