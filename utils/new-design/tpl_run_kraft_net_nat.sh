#!/bin/sh

{{
# Clean up any previous instances.
sudo pkill -f qemu-system
sudo pkill -f firecracker
kraft stop --all
kraft rm --all
}} > /dev/null 2>&1

export KRAFTKIT_BUILDKIT_HOST=docker-container://buildkitd

kraft run \
  --log-level debug --log-type basic \
  --rm \
  {hypervisor_option} \
  --memory {memory} \
  --port {port_ext}:{port_int} \
  --arch {arch} --plat {plat} \
  {target_dir}
