#!/bin/bash

tac Kraftfile | sed '/^\([ \t]\+\)\(CONFIG_.*\)$/ {s/^\([ \t]\+\)\(.*\)$/\1CONFIG_LIBSYSCALL_SHIM_STRACE: '\'y\''\n\1\2/; :loop; n; b loop}' | tac > Kraftfile.strace
tac Kraftfile | sed '/^\([ \t]\+\)\(CONFIG_.*\)$/ {s/^\([ \t]\+\)\(.*\)$/\1CONFIG_LIBSYSCALL_SHIM_STRACE: '\'y\''\n\1CONFIG_LIBUKDEBUG_PRINTK_INFO: '\'y\''\n\1CONFIG_LIBUKDEBUG_PRINTD: '\'y\''\n\1\2/; :loop; n; b loop}' | tac > Kraftfile.debug


test -d ../../kernels/ || mkdir ../../kernels/

rm -f .config*
rm -fr .unikraft

kraft build --no-cache --plat qemu --arch x86_64
cp .unikraft/build/base_qemu-x86_64 ../../kernels/base_qemu-x86_64

kraft build --no-cache --plat fc --arch x86_64
cp .unikraft/build/base_fc-x86_64 ../../kernels/base_fc-x86_64

kraft build -K Kraftfile.strace --no-cache --plat qemu --arch x86_64
cp .unikraft/build/base_qemu-x86_64 ../../kernels/base_qemu-x86_64-strace

kraft build -K Kraftfile.strace --no-cache --plat fc --arch x86_64
cp .unikraft/build/base_fc-x86_64 ../../kernels/base_fc-x86_64-strace

kraft build -K Kraftfile.debug --no-cache --plat qemu --arch x86_64
cp .unikraft/build/base_qemu-x86_64 ../../kernels/base_qemu-x86_64-debug

kraft build -K Kraftfile.debug --no-cache --plat fc --arch x86_64
cp .unikraft/build/base_fc-x86_64 ../../kernels/base_fc-x86_64-debug
