#!/bin/sh

init_rootfs="{rootfs}"

# Use "rootfs" as the actual rootfs directory.
rootfs="{target_dir}/rootfs"
rm -fr "$rootfs"
mkdir "$rootfs"

# If rootfs is Dockerfile, create directory from Dockerfile.
if test "$(basename "$init_rootfs")" = "Dockerfile"; then
    image_name="uk-${name}"
    docker build -o "$rootfs" -f "$init_rootfs" -t "$image_name" .
else
    rootfs="$init_rootfs"
    cp -r "$init_rootfs"/* "$rootfs"
fi

# Create CPIO archive to be used as the embedded initrd.
{base}/unikraft/support/scripts/mkcpio {app_dir}/initrd.cpio "$rootfs"
