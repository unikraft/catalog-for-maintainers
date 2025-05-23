#!/bin/sh

. ./test_common.sh

rm -fr .tests/*
python3 ../../../utils/new-design/all.py ../../../utils/new-design/tester.yaml
for bdir in .tests/*; do
    if test ! -d "$bdir"; then
        continue
    elif test ! -f "$bdir"/build; then
        continue
    fi
    test_one "$bdir"
done
