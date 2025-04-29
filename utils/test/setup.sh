#!/bin/bash

source utils/test/prepare.config

if test $# -ne 1; then
    echo "$0 <dirname>" 1>&2
    exit 1
fi

pushd "$1" > /dev/null 2>&1
mkdir workdir
ln -sfn "$REPO_BASE"/unikraft workdir/unikraft
ln -sfn "$REPO_BASE"/apps workdir/apps
ln -sfn "$REPO_BASE"/libs workdir/libs
popd > /dev/null 2>&1
