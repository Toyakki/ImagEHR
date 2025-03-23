#!/bin/bash

# Install PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -r requirements.txt

# Pull submodules
git submodule update --init --remote --recursive

# Run your app
python3 -m gunicorn -b 0.0.0.0:10000 -w 1 main:app
