#!/usr/bin/env bash

if [[ -n $1 ]]; then
    echo "Start initialisation process for python django tumar application"
    echo "DOMAIN_NAME=tumar."$1 > ./.env
    echo "initialization complete, domain name is tumar."$1
fi
