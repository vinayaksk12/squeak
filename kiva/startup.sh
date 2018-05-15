#!/usr/bin/env bash

BASEDIR=$(dirname $(readlink -f $0))
VENV=venv
ACTIVATE=$VENV/bin/activate
STATUS=false

cd $BASEDIR
if [ ! -d "$VENV" ]; then
  # Control will enter here if $VENV doesn't exist.
  virtualenv $VENV
  STATUS=true
fi
source $ACTIVATE
if [ "$STATUS" = true ]; then
    # if status is true, means need to install all the required libraries
    pip install --upgrade pip
    pip install -r requirements.txt
fi

python scrape_test.py

