#!/bin/bash

for f in $(find -name single_test.sh); do
    d=$(dirname "$f")
    echo -e "## Running in $d\n\n"
    pushd "$d" > /dev/null 2>&1
    ./scripts/test/test.sh
    popd > /dev/null 2>&1
done
