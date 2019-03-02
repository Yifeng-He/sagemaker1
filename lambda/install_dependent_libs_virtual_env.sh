#! /bin/bash

export VIRTUALENV='venv_lambda'
rm -fr $VIRTUALENV

# Setup fresh virtualenv and install requirements
virtualenv $VIRTUALENV
source $VIRTUALENV/bin/activate
pip install -r requirements-lambda.txt
deactivate