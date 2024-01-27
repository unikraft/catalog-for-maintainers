#!/usr/bin/env python

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023, Unikraft GmbH and The Unikraft Authors.

"""Generate run scripts for Unikraft native applications.

Use QEMU, Firecracker and Krafkit for running.
"""

import sys
import os
import stat
import shutil
import yaml


TEMPLATE_SETUP_SCRIPT = """#!/bin/sh

test -d workdir/unikraft || git clone https://github.com/unikraft/unikraft workdir/unikraft

for l in {}; do
    test -d workdir/libs/"$l" || git clone https://github.com/unikraft/lib-"$l" workdir/libs/"$l"
done

test -d workdir/apps/ || git clone https://github.com/unikraft/app-elfloader workdir/apps/elfloader
"""

TEMPLATE_SETUP_NOLIB_SCRIPT = """#!/bin/sh

test -d workdir/unikraft || git clone https://github.com/unikraft/unikraft workdir/unikraft
test -d workdir/apps/ || git clone https://github.com/unikraft/app-elfloader workdir/apps/elfloader
"""

TEMPLATE_BUILD_MAKE = """#!/bin/sh

./scripts/setup.sh
make distclean
UK_DEFCONFIG=$(pwd)/{} make defconfig
touch Makefile.uk
make prepare
make rootfs.cpio
ln -sfn $(pwd)/rootfs.cpio workdir/apps/elfloader/initrd.cpio
make {} -j $(nproc)
test $? -eq 0 && ln -fn workdir/build/{}_{}-{} {}/{}-{}_{}-{}
"""

TEMPLATE_BUILD_KRAFT = """#!/bin/sh

sudo rm -fr .unikraft
rm -f .config.*
kraft build --log-level debug --log-type basic --no-cache --no-update --plat {} --arch {}
test $? -eq 0 && ln -fn .unikraft/build/{}_{}-{} {}/kraft-{}_{}-{}
"""

TEMPLATE_RUN_QEMU_HEADER = """#!/bin/sh

kernel="{}"
cmd="{}"

if test $# -eq 1; then
    kernel="$1"
fi
"""

TEMPLATE_BUILD_MAKEFILE = """UK_ROOT ?= $(PWD)/workdir/unikraft
UK_LIBS ?= $(PWD)/workdir/libs
UK_BUILD ?= $(PWD)/workdir/build
UK_APPS ?= $(PWD)/workdir/apps
APP ?= $(UK_APPS)/elfloader
LIBS ?= {}

all:
	@$(MAKE) -C $(UK_ROOT) A=$(APP) L=$(LIBS) O=$(UK_BUILD)

$(MAKECMDGOALS):
	@$(MAKE) -C $(UK_ROOT) A=$(APP) L=$(LIBS) O=$(UK_BUILD) $(MAKECMDGOALS)

rootfs.cpio:
	test -f Makefile.docker && make -f Makefile.docker rootfs
	./workdir/unikraft/support/scripts/mkcpio $@ rootfs
"""

RUN_COMMON_NET_COMMANDS = """
# Remove previously created network interfaces.
sudo ip link set dev tap0 down 2> /dev/null
sudo ip link del dev tap0 2> /dev/null
sudo ip link set dev virbr0 down 2> /dev/null
sudo ip link del dev virbr0 2> /dev/null
"""

RUN_QEMU_NET_COMMANDS = """
# Create bridge interface for QEMU networking.
sudo ip link add dev virbr0 type bridge
sudo ip address add 172.44.0.1/24 dev virbr0
sudo ip link set dev virbr0 up
"""

RUN_FIRECRACKER_NET_COMMANDS = """
# Create tap interface for Firecracker networking.
sudo ip tuntap add dev tap0 mode tap
sudo ip address add 172.44.0.1/24 dev tap0
sudo ip link set dev tap0 up
"""

RUN_KRAFT_NET_COMMANDS = """
# Create bridge interface for KraftKit networking.
sudo kraft net create -n 172.44.0.1/24 virbr0
"""

TEMPLATE_RUN_FIRECRACKER_HEADER = """#!/bin/sh

config="{}"

if test $# -eq 1; then
    config="$1"
fi
"""

RUN_FIRECRACKER_PREPARE = """
# Remove previously created files.
sudo rm -f /tmp/firecracker.log
touch /tmp/firecracker.log
sudo rm -f /tmp/firecracker.socket
"""

RUN_FIRECRACKER_COMMAND = """firecracker-x86_64 \\
        --api-sock /tmp/firecracker.socket \\
        --config-file "$config"
"""

RUN_KRAFT_HEADER = """#!/bin/sh
"""

RUN_KILL_COMMANDS = """
# Clean up any previous instances.
sudo pkill -f qemu-system 2> /dev/null
sudo pkill -f firecracker 2> /dev/null
sudo kraft stop --all 2> /dev/null
sudo kraft rm --all 2> /dev/null
"""

TEMPLATE_RUN_CPIO_COMMANDS = """
rootfs={}

# Create CPIO archive to be used as the initrd.
./workdir/unikraft/support/scripts/mkcpio initrd.cpio "$rootfs"
"""


DEFCONFIG = "defconfig"
SCRIPTS = "scripts"
BUILD = "build"
RUN = "run"
KERNEL = "kernel"
CONFIG = "config.yaml"
KRAFTCONFIG = "Kraftfile"


def files(path):
    """Extract regular files in given directory.

    Ignore directories or other file types.
    """

    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(os.path.join(path, file)):
            yield file_path


def generate_setup(config):
    """Generate shell script to set up repositories."""

    if config['libs']:
        contents = TEMPLATE_SETUP_SCRIPT.format(" ".join(l for l in config['libs']))
    else:
        contents = TEMPLATE_SETUP_NOLIB_SCRIPT

    out_file = os.path.join(config['scriptsdir'], "setup.sh")
    with open(out_file, "w", encoding="utf-8") as stream:
        stream.write(contents)
    sbuf = os.stat(out_file)
    os.chmod(out_file, sbuf.st_mode | stat.S_IEXEC)


def generate_defconfig(config):
    """Generate default configuration files for Make-basd builds."""

    for target in config['targets']:
        out_file = os.path.join(config['defconfigdir'], f"{target['plat']}-{target['arch']}")
        with open(out_file, "w", encoding="utf-8") as stream:
            stream.write(f"CONFIG_UK_NAME=\"{config['name']}\"\n")
            stream.write(f"CONFIG_UK_DEFNAME=\"{config['name']}\"\n")
            if target['plat'] == 'qemu':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_QEMU=y\n")
            if target['plat'] == 'fc' or target['plat'] == 'firecracker':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_FIRECRACKER=y\n")
            if target['arch'] == 'arm64':
                stream.write("CONFIG_ARCH_ARM_64=y\n")
                stream.write("CONFIG_ARM64_ERRATUM_858921=n\n")
                stream.write("CONFIG_ARM64_ERRATUM_835769=n\n")
                stream.write("CONFIG_ARM64_ERRATUM_843419=n\n")
            if target['arch'] == 'x86_64':
                stream.write("CONFIG_ARCH_X86_64=y\n")
            for lib in config['libs']:
                stream.write("CONFIG_LIB{}=y\n".format(lib.replace('-', '_').upper()))
            for key, value in config['kconfig'].items():
                stream.write(f"{key}={value}\n")


def generate_build_makefile(config):
    """Generate Makefile to build kernel (with Make)."""

    if config['libs']:
        contents = TEMPLATE_BUILD_MAKEFILE.format(
                ":".join(f"$(UK_LIBS)/{lib}" for lib in config['libs'])
                )
    else:
        contents = TEMPLATE_BUILD_MAKEFILE.format("")

    with open("Makefile", "w", encoding="utf-8") as stream:
        stream.write(contents)


def generate_build_make(config, defconfig, plat, arch):
    """Generate build scripts using Make.

    Scripts are generated in scripts/build/ directory and start
    with the `make-` prefix.
    """

    for compiler in config['compilers'][arch]:
        compiler_version = compiler.split("-")[-1]
        if "gcc" in compiler:
            compiler_name = f"gcc-{compiler_version}"
        if "clang" in compiler:
            compiler_name = f"clang-{compiler_version}"
        compiler_var = f"COMPILER={compiler_name}"

        contents = TEMPLATE_BUILD_MAKE.format(defconfig, compiler_var, config['name'], plat, arch,
                                              config['kerneldir'],
                                              compiler_name, config['name'], plat, arch)
        base = os.path.basename(defconfig)
        out_file = os.path.join(config['builddir'], f"make-{compiler_name}-{base}.sh")
        with open(out_file, "w", encoding="utf8") as stream:
            stream.write(contents)
        sbuf = os.stat(out_file)
        os.chmod(out_file, sbuf.st_mode | stat.S_IEXEC)


def generate_build_kraft(config, plat, arch):
    """Generate build scripts using Kraftkit.

    Scripts are generated in scripts/build/ directory and start
    with the `kraft-` prefix.
    """

    contents = TEMPLATE_BUILD_KRAFT.format(plat, arch,
                                           config['name'], plat, arch,
                                           config['kerneldir'], config['name'], plat, arch)
    out_file = os.path.join(config['builddir'], f"kraft-{plat}-{arch}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(contents)
    sbuf = os.stat(out_file)
    os.chmod(out_file, sbuf.st_mode | stat.S_IEXEC)


def generate_build(config):
    """Generate build scripts.

    Scripts are generated in scripts/build/ directory.
    """

    generate_build_makefile(config)

    # Generate make-based build scripts from defconfigs.
    for file in files(config['defconfigdir']):
        plat, arch = os.path.basename(file).split("-")
        generate_build_make(config, file, plat, arch)

    for target in config['targets']:
        generate_build_kraft(config, target['plat'], target['arch'])


def generate_run_fc_json(config, plat, arch, compiler, filesystem):
    """Generate running config (JSON) for Firecracker."""

    kernel = os.path.join(config['kerneldir'], f"{compiler}-{config['name']}_{plat}-{arch}")

    json_name = os.path.join(config['rundir'], f"{compiler}-{plat}-{arch}-{filesystem}.json")
    with open(json_name, "w", encoding="utf8") as stream:
        stream.write("{\n")
        stream.write('  "boot-source": {\n')
        stream.write(f'    "kernel_image_path": "{kernel}",\n')
        stream.write(f'    "boot_args": "{kernel} ')
        if config['networking']:
            stream.write("netdev.ip=172.44.0.2/24:172.44.0.1 ")
        if config['rootfs']:
            stream.write('vfs.fstab=[ \\"initrd:/:initrd::extract:\\" ] ')
        if config['cmd']:
            stream.write(f"-- {config['cmd']}\"")
        else:
            stream.write("-- template")
        if config['rootfs']:
            stream.write(',\n    "initrd_path": "initrd.cpio"')
        stream.write("\n  },\n")
        stream.write(
            f"""  "drives": [],
  "machine-config": {{
    "vcpu_count": 1,
    "mem_size_mib": {config['memory']},
    "smt": false,
    "track_dirty_pages": false
  }},
  "cpu-config": null,
  "balloon": null,
"""
        )
        if config['networking']:
            stream.write(
                """  "network-interfaces": [
    {
      "iface_id": "net1",
      "guest_mac":  "06:00:ac:10:00:02",
      "host_dev_name": "tap0"
    }
  ],
"""
            )
        stream.write(
            """  "vsock": null,
  "logger": {
    "log_path": "/tmp/firecracker.log",
    "level": "Debug",
    "show_level": true,
    "show_log_origin": true
  },
  "metrics": null,
  "mmds-config": null,
  "entropy": null
}
"""
        )


def generate_run_fc(config, plat, arch, compiler, filesystem):
    """Generate running script using Firecracker."""

    header = TEMPLATE_RUN_FIRECRACKER_HEADER.format(
            os.path.join(f"{config['rundir']}", f"{compiler}-{plat}-{arch}-{filesystem}.json")
            )

    out_file = os.path.join(config['rundir'], f"{compiler}-{plat}-{arch}-{filesystem}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(header)
        stream.write(RUN_KILL_COMMANDS)
        if config['networking']:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_FIRECRACKER_NET_COMMANDS)
        if config['rootfs']:
            if filesystem == "initrd":
                stream.write(TEMPLATE_RUN_CPIO_COMMANDS.format(f"{config['rootfs']}"))
        stream.write(RUN_FIRECRACKER_PREPARE)
        if config['networking']:
            stream.write("sudo ")
        stream.write(RUN_FIRECRACKER_COMMAND)
        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run_qemu(config, plat, arch, compiler, filesystem):
    """Generate running script using QEMU."""

    kernel = os.path.join(config['kerneldir'], f"{compiler}-{config['name']}_{plat}-{arch}")

    if config['cmd']:
        header = TEMPLATE_RUN_QEMU_HEADER.format(kernel, config['cmd'])
    else:
        header = TEMPLATE_RUN_QEMU_HEADER.format(kernel, "")

    out_file = os.path.join(config['rundir'], f"{compiler}-{plat}-{arch}-{filesystem}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(header)
        stream.write(RUN_KILL_COMMANDS)
        if config['networking']:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_QEMU_NET_COMMANDS)
        stream.write("\n")
        if config['rootfs']:
            if filesystem == "initrd":
                stream.write(TEMPLATE_RUN_CPIO_COMMANDS.format(f"{config['rootfs']}"))
        if config['networking']:
            stream.write("sudo ")
        if arch == "x86_64":
            stream.write("qemu-system-x86_64 \\\n")
            if 'accel' in config.keys():
                if config['accel']:
                    stream.write("    -accel kvm \\\n")
        else:
            stream.write("qemu-system-aarch64 \\\n")
            stream.write("    -machine virt \\\n")
        stream.write('    -kernel "$kernel" \\\n')
        stream.write("    -nographic \\\n")
        stream.write(f"    -m {config['memory']}M \\\n")
        if config['networking']:
            stream.write("    -netdev bridge,id=en0,br=virbr0 ")
            stream.write("-device virtio-net-pci,netdev=en0 \\\n")
            stream.write('    -append "netdev.ip=172.44.0.2/24:172.44.0.1 ')
            if config['rootfs']:
                if filesystem == "initrd":
                    stream.write('vfs.fstab=[ \\"initrd0:/:extract:::\\" ] ')
                elif filesystem == "9pfs":
                    stream.write('vfs.fstab=[ \\"9pfs:/:fs0::extract:\\" ] ')
            stream.write('-- $cmd" \\\n')
        else:
            stream.write('    -append "')
            if config['rootfs']:
                if filesystem == "initrd":
                    stream.write('vfs.fstab=[ \\"initrd0:/:extract:::\\" ] ')
                elif filesystem == "9pfs":
                    stream.write('vfs.fstab=[ \\"9pfs:/:fs0::extract:\\" ] ')
            stream.write('-- $cmd" \\\n')
        if config['rootfs']:
            if filesystem == "initrd":
                stream.write('    -initrd "$PWD"/initrd.cpio \\\n')
            elif filesystem == "9pfs":
                stream.write("    -fsdev local,id=myid,path=\"$rootfs\",security_model=none \\\n")
                stream.write("    -device virtio-9p-pci,fsdev=myid,mount_tag=fs0,")
        stream.write("    -cpu max\n")
        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run_kraft(config, plat, arch, filesystem):
    """Generate running script using KraftKit."""

    out_file = os.path.join(config['rundir'], f"kraft-{plat}-{arch}-{filesystem}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(RUN_KRAFT_HEADER)
        stream.write(RUN_KILL_COMMANDS)
        if config['networking']:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_KRAFT_NET_COMMANDS)
        stream.write("\n")
        if config['networking']:
            stream.write("sudo ")
        stream.write(
            "KRAFTKIT_BUILDKIT_HOST=docker-container://buildkitd kraft run \\\n"
        )
        if 'accel' not in config.keys():
            stream.write("    -W \\\n")
        elif not config['accel']:
            stream.write("    -W \\\n")
        elif arch == "arm64":
            stream.write("    -W \\\n")
        stream.write(f"    --memory {config['memory']}M \\\n")
        stream.write("    --log-level debug --log-type basic \\\n")
        if config['networking']:
            stream.write("    --network bridge:virbr0 \\\n")
        stream.write(f"    --arch {arch} --plat {plat}\n")

        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run(config):
    """Generate running scripts."""

    for target in config['targets']:
        for compiler in config['compilers'][target['arch']]:
            compiler_version = compiler.split("-")[-1]
            if "gcc" in compiler:
                compiler_name = f"gcc-{compiler_version}"
            if "clang" in compiler:
                compiler_name = f"clang-{compiler_version}"

            if target['plat'] == "fc" or \
                    target['plat'] == "firecracker" or \
                    target['plat'] == "kraftcloud":
                if config['rootfs']:
                    generate_run_fc_json(config, target['plat'], target['arch'], compiler_name, "initrd")
                    generate_run_fc(config, target['plat'], target['arch'], compiler_name, "initrd")
                else:
                    generate_run_fc_json(config, target['plat'], target['arch'], compiler_name, "nofs")
                    generate_run_fc(config, target['plat'], target['arch'], compiler_name, "nofs")
            elif target['plat'] == "qemu":
                if config['rootfs']:
                    generate_run_qemu(config, target['plat'], target['arch'], compiler_name, "initrd")
                    generate_run_qemu(config, target['plat'], target['arch'], compiler_name, "9pfs")
                else:
                    generate_run_qemu(config, target['plat'], target['arch'], compiler_name, "nofs")

    for target in config['targets']:
        generate_run_kraft(config, target['plat'], target['arch'], "nofs")


def get_compilers(config):
    """Get list of compilers available on the system."""

    # XXX: For now assume an x86 system.
    config['compilers'] = {
            'x86_64': [],
            'arm64': []
            }
    for version in range(5, 30):
        if shutil.which(f"gcc-{version}"):
            config['compilers']['x86_64'].append(f"gcc-{version}")
        if shutil.which(f"aarch64-linux-gnu-gcc-{version}"):
            config['compilers']['arm64'].append(f"aarch64-linux-gnu-gcc-{version}")
    for version in range(9, 30):
        if shutil.which(f"clang-{version}"):
            config['compilers']['x86_64'].append(f"clang-{version}")
            config['compilers']['arm64'].append(f"clang-{version}")


def main():
    """The main program function calls generate functions."""

    # Obtain configurations for running applications.
    try:
        with open(CONFIG, "r", encoding="utf8") as stream:
            config = yaml.safe_load(stream)
    except IOError:
        print(f"Error: Unable to open configuration file '{CONFIG}'", file=sys.stderr)
        sys.exit(1)

    if not 'memory' in config.keys():
        print(f"Error: 'memory' attribute is not defined in '{CONFIG}'", file=sys.stderr)
        sys.exit(1)

    if not 'rootfs' in config.keys():
        config['rootfs'] = None
    if not 'networking' in config.keys():
        config['networking'] = None
    if not 'scriptsdir' in config.keys():
        config['scriptsdir'] = SCRIPTS
    if not 'defconfigdir' in config.keys():
        config['defconfigdir'] = os.path.join(config['scriptsdir'], DEFCONFIG)
    if not 'builddir' in config.keys():
        config['builddir'] = os.path.join(config['scriptsdir'], BUILD)
    if not 'rundir' in config.keys():
        config['rundir'] = os.path.join(config['scriptsdir'], RUN)
    if not 'kerneldir' in config.keys():
        config['kerneldir'] = os.path.join(config['scriptsdir'], KERNEL)

    if not os.path.exists(config['scriptsdir']):
        os.mkdir(config['scriptsdir'])
    if not os.path.exists(config['defconfigdir']):
        os.mkdir(config['defconfigdir'])
    if not os.path.exists(config['builddir']):
        os.mkdir(config['builddir'])
    if not os.path.exists(config['rundir']):
        os.mkdir(config['rundir'])
    if not os.path.exists(config['kerneldir']):
        os.mkdir(config['kerneldir'])

    try:
        with os.scandir(config['scriptsdir']) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['scriptsdir']}'",
              file=sys.stderr)
    try:
        with os.scandir(config['defconfigdir']) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['defconfigdir']}'",
              file=sys.stderr)
    try:
        with os.scandir(config['builddir']) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['builddir']}'",
              file=sys.stderr)
    try:
        with os.scandir(config['rundir']) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['rundir']}'",
              file=sys.stderr)

    # Parse KraftKit config file (usually Kraftfile).
    try:
        with open(KRAFTCONFIG, "r", encoding="utf8") as stream:
            data = yaml.safe_load(stream)
    except IOError:
        print(f"Error: Unable to open Kraft configuration file '{KRAFTCONFIG}'",
              file=sys.stderr)
        sys.exit(1)

    if not 'name' in data.keys():
        print(f"Error: 'name' attribute is not defined in '{KRAFTCONFIG}'",
              file=sys.stderr)
        sys.exit(1)
    config['name'] = data['name']

    if not 'cmd' in data.keys():
        config['cmd'] = None
    else:
        config['cmd'] = " ".join(c for c in data['cmd'])

    config['kconfig'] = data['unikraft']['kconfig']

    if not "libraries" in data.keys():
        config['libs'] = None
    else:
        config['libs'] = list(data['libraries'].keys())
        for lib in config['libs']:
            if isinstance(data['libraries'][lib], dict):
                if "kconfig" in data['libraries'][lib].keys():
                    config['kconfig'].update(data['libraries'][lib]['kconfig'])

    config['targets'] = []
    for target in data['targets']:
        plat, arch = target.split('/')
        config['targets'].append({
            'plat': plat,
            'arch': arch})

    get_compilers(config)

    generate_setup(config)
    generate_defconfig(config)
    generate_build(config)
    generate_run(config)


if __name__ == "__main__":
    sys.exit(main())
