#!/bin/bash

set -a # automatically export all variables
. .env
set +a

# wait for Postgres to start
function postgres_ready() {
python << END
import sys
import os
import psycopg2
from urllib.parse import urlparse

result = urlparse(os.getenv("TUMAR_DB"))
dbname = result.path[1:]
user = result.username
password = result.password
host = result.hostname
port = result.port
print(result)
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Start app
>&2 echo "Postgres is up - executing command"

./start.sh