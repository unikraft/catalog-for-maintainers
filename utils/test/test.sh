#!/bin/bash

source scripts/test/config

is_in_array()
{
    needle="$1"
    haystack="$2"

    found=0
    for item in ${haystack[@]}; do
        if test "$needle" = "$item"; then
            found=1
            break
        fi
    done

    return "$found"
}

out_dir="scripts/test/$(date +"%Y-%m-%d-%H:%M:%S")"
mkdir "$out_dir"
for b in ${BUILD_SCRIPTS[@]}; do
    build_script="scripts/build/$b"
    bbase="$(basename "$build_script" .sh)"
    build_tool=${bbase%%-*}
    rest=${bbase#*-}
    plat=${rest%%-*}
    rest=${rest#*-}
    arch=${rest%%-*}
    rest=${rest#*-}
    einitrd=${rest%%-*}

    if test "$build_tool" = "kraft"; then
        # KraftKit run steps require KraftKit build steps.
        if test -z "$SKIP_BUILD" -o "$SKIP_BUILD" -eq 0; then
            per_build_run_scripts=$(ls scripts/run/kraft-"$plat-$arch"-*.sh)
        fi
    else
        if test "$einitrd" = "einitrd"; then
            per_build_run_scripts=$(ls scripts/run/"$plat-$arch"-einitrd-{9pfs,initrd,nofs}.sh 2> /dev/null)
        else
            per_build_run_scripts=$(ls scripts/run/"$plat-$arch"-{9pfs,initrd,nofs}.sh 2> /dev/null)
        fi
    fi
    if test -z "$per_build_run_scripts"; then
        continue
    fi

    if test -z "$SKIP_BUILD" -o "$SKIP_BUILD" -eq 0; then
        printf "[build] %-50s ... " ${bbase:0:50}
        "$build_script" > "$out_dir"/build-"$bbase".log 2>&1
        test $? -eq 0 && echo "PASSED" || echo "FAILED"
    fi

    if test ! -z "$SKIP_RUN" -a "$SKIP_RUN" -eq 1; then
        continue
    fi

    for r in $per_build_run_scripts; do
        rbase="$(basename "$r" .sh)"
        is_in_array "$rbase".sh "$RUN_SCRIPTS"
        if test $? -eq 0; then
            continue
        fi
        printf "[run]   %-50s ... " ${rbase:0:50}
        ./single_test.sh "$r" > "$out_dir"/run-"$rbase".log 2>&1
        test $? -eq 0 && echo "PASSED" || echo "FAILED"
    done
done
