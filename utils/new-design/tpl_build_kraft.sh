#!/bin/sh

init_rootfs="{rootfs}"
rootfs="{target_dir}/rootfs"

if test ! -z "$rootfs"; then
    if test ! "$(basename "$init_rootfs")" = "Dockerfile"; then
        rm -fr "$rootfs"
        cp -r "$init_rootfs" "$rootfs"
    fi
fi

rm -fr {target_dir}/.unikraft/build
rm -f {target_dir}/.config.*
kraft build --log-level debug --log-type basic --no-cache --no-update --plat {plat} --arch {arch} {target_dir}
