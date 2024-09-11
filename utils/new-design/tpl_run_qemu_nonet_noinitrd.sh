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

{vmm} \
    {hypervisor_option} \
    -kernel "$kernel" \
    -nographic \
    -m {memory} \
    -append "{name} -- $cmd" \
    -cpu max
