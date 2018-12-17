#!/bin/bash
#TEST=True
#export TEST

BASEDIR=$(dirname $(readlink -f $0))
VENV=venv/bin/activate

cd $BASEDIR
source $VENV
cd ..
python __init__.py
