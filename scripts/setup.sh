#!/bin/bash
echo ""
echo "This may take a while"

echo "Creating virtual environment"
python3 -m venv env

echo "Installing requirements.txt"
env/bin/pip install -r requirements.txt
