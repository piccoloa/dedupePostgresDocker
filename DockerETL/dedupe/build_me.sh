#!/bin/sh

# Make sure we're in same path as this build_me.sh script
cd "$(dirname "$(realpath "$0")")";

# cython src/*.pyx && pip install -e . && pytest tests --cov dedupe && python tests/canonical.py -vv
# PIP install handled as part of Dockerfile & ../requirements.txt -- let's not re-invent the wheel again
cython src/*.pyx && python setup.py install && pytest tests --cov dedupe && python tests/canonical.py -vv