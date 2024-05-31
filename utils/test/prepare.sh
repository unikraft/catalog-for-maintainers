#!/bin/bash

source utils/test/prepare.config

if test $# -ne 1; then
    echo "$0 <dirname>" 1>&2
    exit 1
fi

pushd "$1" > /dev/null 2>&1
sed -i 's|^\([ \t]\)*version:|\1 #version:|g' Kraftfile
sed -i 's|^\([ \t]\)*source: \(.*/unikraft/\?\)$|\1 source: '"$REPO_BASE/unikraft"'\n\1 #source: \2|g' Kraftfile
sed -i 's|^\([ \t]\)*source: \(.*/\)lib-\([^\.]\+\)\(.*\)$|\1 source: '"$REPO_BASE/libs/"'\3\n\1 #source: \2lib-\3\4|g' Kraftfile
sed -i 's|^\([ \t]\)*source: \(.*/\)app-\([^\.]\+\)\(.*\)$|\1 source: '"$REPO_BASE/apps/"'\3\n\1 #source: \2app-\3\4|g' Kraftfile
popd > /dev/null 2>&1
