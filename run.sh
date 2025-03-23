#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Pull submodules
git submodule update --init --remote --recursive

# Run your app
python3 gunicorn main:app
