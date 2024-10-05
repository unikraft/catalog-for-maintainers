#!/bin/sh

kernel="{kernel}"
cmd="{cmd}"

if test $# -eq 1; then
    kernel="$1"
fi

{{
# Clean up any previous instances.
sudo pkill -f qemu-system
sudo pkill -f firecracker
kraft stop --all
kraft rm --all
}} > /dev/null 2>&1

rootfs={target_dir}/rootfs

# Create CPIO archive to be used as the initrd.
{base}/unikraft/support/scripts/mkcpio {run_dir}/initrd.cpio "$rootfs"
{vmm} \
    {hypervisor_option} \
    {machine} \
    -kernel "$kernel" \
    -nographic \
    -m {memory} \
    -append "{name} vfs.fstab=[ \"initrd0:/:extract::ramfs=1:\" ] -- $cmd" \
    -initrd {run_dir}/initrd.cpio \
    -cpu max
