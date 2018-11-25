#! /bin/bash

if [[ $(python --version 2>&1) =~ 2\.7 ]]; then
    # Python2
    flake8 --statistics --show-source --exclude prototype
    python -m unittest discover -s tests
else
    # Python3
    flake8 --statistics --show-source prototype
    python -m unittest discover -s prototype
fi