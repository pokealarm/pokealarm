#!/usr/bin/env bash

if [[ $(python --version 2>&1) =~ 2\.7 ]]; then
    # Python2
    flake8 --statistics --show-source --exclude pokealarmv4
    python -m unittest discover -s tests
else
    # Python3
    flake8 --statistics --show-source pokealarmv4
    python -m unittest discover -s testsv4
fi