#!/bin/sh

. ./test_common.sh

if test $# -ne 1; then
    echo "Wrong arguments." 1>&2
    echo "$0 path/to/test/directory" 1>&2
    exit 1
fi

run_run_scripts "$1"
