#!/bin/bash

BASEDIR=$(dirname $(readlink -f $0))
DIRECTORY=venv
VENV=venv/bin/activate

cd $BASEDIR
cd ..
if [ ! -d "$DIRECTORY" ]; then
  # Control will enter here if $DIRECTORY does not exists.
  virtualenv $DIRECTORY
  source $VENV
  pip install -r $BASEDIR/requirements.txt
  pip install pip --upgrade
  pip install python-dateutil --upgrade
  deactivate
fi

source $VENV
cd sweep
scrapy crawl zaubacorp -s LOG_LEVEL=WARNING -t json 2> logs/sweep.log
