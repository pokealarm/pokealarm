#!/usr/bin/env bash

if [[ $(python --version 2>&1) =~ 2\.7 ]]; then
    # Python2
    pip install -r requirements.txt
else
    # Python3
    pip install -r requirementsv4.txt
fi