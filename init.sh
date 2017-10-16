#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"

fatal () {
    echo "FATAL: ${*}"
    exit 1
}

if [[ ! -d .env ]]; then
    echo "virtualenv missing, initializing..."
    python3 -m venv .env
    source .env/bin/activate
    if [[ -f requirements.txt ]]; then
        pip install -r requirements.txt
    fi
else
    source .env/bin/activate
fi