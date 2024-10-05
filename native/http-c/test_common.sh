#!/bin/bash

run_build_script()
{
    bdir="${1%/}"

    if test ! -d "$bdir"; then
        echo "$bdir is not a directory"
        return
    elif test ! -f "$bdir"/build; then
        echo "No build script in $bdir"
        return
    fi
    echo -n "Building $bdir ...     "
    "$bdir"/build > "$bdir"/build.log 2>&1
}

run_run_scripts()
{
    bdir="${1%/}"

    for rdir in "$bdir"/run-*; do
        if test ! -d "$rdir"; then
            continue
        elif test ! -f "$rdir"/run; then
            continue
        else
            echo -n "    Using $rdir ... "
            grep "networking: nat" "$rdir"/config.yaml > /dev/null 2>&1
            if test $? -eq 0; then
                ./.test "$rdir"/run 127.0.0.1 8080 2> "$rdir"/run.log
            else
                ./.test "$rdir"/run 172.44.0.2 8080 2> "$rdir"/run.log
            fi
        fi
    done
}

test_one()
{
    bdir="${1%/}"

    # Clean up.
    rm -fr "$bdir"/.unikraft

    # Run build script.
    run_build_script "$bdir"
    build_exitcode=$?
    if test "$build_exitcode" -eq 0; then
        echo "PASSED"
    else
        echo "FAILED"
    fi

    # Run run scripts.
    run_run_scripts "$bdir"
}
