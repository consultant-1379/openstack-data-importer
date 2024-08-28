#!/bin/bash

time docker build -f testsuite/Dockerfile . -t importertest
if [[ $? -ne 0 ]]
then
    exit 1
fi

time docker run --rm -t importertest ./code_style_checks.sh
if [[ $? -ne 0 ]]
then
    exit 1
fi
