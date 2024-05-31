#!/bin/bash

for f in $(find -name config.yaml); do
    d=$(dirname "$f")
    echo -e "## Running in $d\n\n"
    pushd "$d" > /dev/null 2>&1
    test -f ../../../utils/native/generate.py && ../../../utils/native/generate.py
    test -f ../../utils/native/generate.py && ../../utils/native/generate.py
    popd > /dev/null 2>&1
done
