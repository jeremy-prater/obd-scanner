#!/bin/bash

python3 -m venv ./build

source ./build/bin/activate

pip3 install coloredlogs
pip3 install pyftdi
pip3 install pint
