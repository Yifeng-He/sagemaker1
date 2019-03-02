#! /bin/bash

export VIRTUALENV='venv_lambda'
export ZIP_FILE='lambda.zip'
export PYTHON_VERSION='python2.7'

# Zip dependencies from virtualenv, and main.py
cd $VIRTUALENV/lib/$PYTHON_VERSION/site-packages/
zip -r9 ../../../../$ZIP_FILE *
cd ../../../../
zip -g $ZIP_FILE main.py