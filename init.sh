#!/usr/bin/env bash

if [[ -n $1 ]]; then
    echo "Start initialisation process for python django arys application"
    echo "DOMAIN_NAME=arys."$1 > ./.env
    echo "initialization complete, domain name is arys."$1
fi
