#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Update submodules
git submodule update --init --remote --recursive

# Run your app
python main.py
