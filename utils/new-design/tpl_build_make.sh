#!/bin/sh

make distclean
UK_DEFCONFIG={target_dir}/defconfig make defconfig
touch Makefile.uk
make prepare
make -j $(nproc)
