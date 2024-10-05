#!/usr/bin/env python3

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023, Unikraft GmbH and The Unikraft Authors.

"""Generate run scripts for Unikraft native applications.

Use QEMU, Firecracker and Krafkit for running.
"""

import sys
import os
import shutil
import stat
import yaml


TEMPLATE_SETUP_SCRIPT_NO_LIBS = """#!/bin/sh

test -d workdir/unikraft || git clone https://github.com/unikraft/unikraft workdir/unikraft

ln -sfn workdir .unikraft
"""

TEMPLATE_SETUP_SCRIPT = """#!/bin/sh

test -d workdir/unikraft || git clone https://github.com/unikraft/unikraft workdir/unikraft

for l in {}; do
    test -d workdir/libs/"$l" || git clone https://github.com/unikraft/lib-"$l" workdir/libs/"$l"
done

ln -sfn workdir .unikraft
"""

TEMPLATE_SETUP_SCRIPT_TEMPLATE_APP = """#!/bin/sh

test -d workdir/unikraft || git clone https://github.com/unikraft/unikraft workdir/unikraft

for l in {}; do
    test -d workdir/libs/"$l" || git clone https://github.com/unikraft/lib-"$l" workdir/libs/"$l"
done

test -d workdir/apps/{} || git clone {} workdir/apps/{}

ln -sfn workdir .unikraft
"""

TEMPLATE_BUILD_MAKE = """#!/bin/sh

make distclean
UK_DEFCONFIG=$(pwd)/scripts/defconfig/{} make defconfig
touch Makefile.uk
make prepare
make -j $(nproc)
test $? -eq 0 && ln -fn workdir/build/{}
"""

TEMPLATE_BUILD_MAKE_EINITRD = """#!/bin/bash
{}
# Create CPIO archive to be used as the embedded initrd.
rootfs={}
"$PWD"/workdir/unikraft/support/scripts/mkcpio {}/initrd.cpio "$rootfs"

make distclean
UK_DEFCONFIG=$(pwd)/scripts/defconfig/{} make defconfig
touch Makefile.uk
make prepare
make -j $(nproc)
test $? -eq 0 && ln -fn workdir/build/{}
"""

TEMPLATE_BUILD_KRAFT = """#!/bin/sh

rm -fr .unikraft/build
rm -f .config.*
KRAFTKIT_BUILDKIT_HOST=docker-container://buildkitd kraft build --log-level debug --log-type basic --no-cache --no-update --plat {} --arch {}
test $? -eq 0 && ln -fn .unikraft/build/{}_{}-{} kraft-{}_{}-{}
"""

TEMPLATE_RUN_QEMU_HEADER = """#!/bin/sh

kernel="{}"
cmd="{}"

if test $# -eq 1; then
    kernel="$1"
fi
"""

TEMPLATE_BUILD_MAKEFILE = """UK_APP ?= {}
UK_ROOT ?= $(PWD)/workdir/unikraft
UK_LIBS ?= $(PWD)/workdir/libs
UK_BUILD ?= $(PWD)/workdir/build
LIBS ?= {}

all:
	@$(MAKE) -C $(UK_ROOT) A=$(UK_APP) L=$(LIBS) O=$(UK_BUILD)

$(MAKECMDGOALS):
	@$(MAKE) -C $(UK_ROOT) A=$(UK_APP) L=$(LIBS) O=$(UK_BUILD) $(MAKECMDGOALS)
"""

RUN_COMMON_NET_COMMANDS = """
{
# Remove previously created network interfaces.
sudo ip link set dev tap0 down
sudo ip link del dev tap0
sudo ip link set dev virbr0 down
sudo ip link del dev virbr0
} > /dev/null 2>&1
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
sudo KRAFTKIT_NO_WARN_SUDO=1 kraft net create -n 172.44.0.1/24 virbr0
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

RUN_FIRECRACKER_COMMAND = """{} \\
        --api-sock /tmp/firecracker.socket \\
        --config-file "$config"
"""

RUN_KRAFT_HEADER = """#!/bin/sh
"""

RUN_KILL_COMMANDS = """
{
# Clean up any previous instances.
sudo pkill -f qemu-system
sudo pkill -f firecracker
kraft stop --all
kraft rm --all
sudo KRAFTKIT_NO_WARN_SUDO=1 kraft stop --all
sudo KRAFTKIT_NO_WARN_SUDO=1 kraft rm --all
} > /dev/null 2>&1
"""

TEMPLATE_RUN_CPIO_COMMANDS = """
rootfs={}

# Create CPIO archive to be used as the initrd.
"$PWD"/workdir/unikraft/support/scripts/mkcpio initrd.cpio "$rootfs"
"""

TEMPLATE_RUN_9PFS_COMMANDS = """
rootfs=9pfs-"$(basename {})"

# Create a fresh filesystem copy to use.
rm -fr "$rootfs"
cp -r {} "$rootfs"
"""

TEMPLATE_RUN_DOCKER_EXPORT = """
IMAGE_NAME=unikraft-{} make -f {} export
"""


DEFCONFIG = "defconfig"
SCRIPTS = "scripts"
BUILD = "build"
RUN = "run"
TEST = "test"
DOCKER = "docker"
DOCKER_MAKEFILE = "docker.Makefile"
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

    if config["libs"]:
        if config["template"]:
            contents = TEMPLATE_SETUP_SCRIPT_TEMPLATE_APP.format(" ".join(l for l in config["libs"]), \
                    config["template_name"], config["template"], config["template_name"])
        else:
            contents = TEMPLATE_SETUP_SCRIPT.format(" ".join(l for l in config["libs"]))
    else:
        contents = TEMPLATE_SETUP_SCRIPT_NO_LIBS

    out_file = os.path.join(config["scriptsdir"], "setup.sh")
    with open(out_file, "w", encoding="utf-8") as stream:
        stream.write(contents)
    st = os.stat(out_file)
    os.chmod(out_file, st.st_mode | stat.S_IEXEC)


def generate_defconfig(config):
    """Generate default configuration files for Make-based builds."""

    for t in config["targets"]:
        if t["einitrd"]:
            out_file = os.path.join(config["defconfigdir"], f"{t['plat']}-{t['arch']}-einitrd")
        else:
            out_file = os.path.join(config["defconfigdir"], f"{t['plat']}-{t['arch']}")
        with open(out_file, "w", encoding="utf-8") as stream:
            stream.write(f"CONFIG_UK_NAME=\"{t['name']}\"\n")
            stream.write(f"CONFIG_UK_DEFNAME=\"{t['name']}\"\n")
            if t["einitrd"]:
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD=y\n")
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI=y\n")
            else:
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD=n\n")
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI=n\n")
            if t['plat'] == 'qemu':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_QEMU=y\n")
            if t['plat'] == 'fc' or t['plat'] == 'firecracker':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_FIRECRACKER=y\n")
            if t['arch'] == 'arm64':
                stream.write("CONFIG_ARCH_ARM_64=y\n")
            if t['arch'] == 'x86_64':
                stream.write("CONFIG_ARCH_X86_64=y\n")
            if config["libs"]:
                for l in config["libs"]:
                    if l.startswith("lib"):
                        stream.write("CONFIG_{}=y\n".format(l.replace('-', '_').upper()))
                    else:
                        stream.write("CONFIG_LIB{}=y\n".format(l.replace('-', '_').upper()))
            for k, v in config["kconfig"].items():
                stream.write(f"{k}={v}\n")


def generate_build_makefile(config):
    """Generate Makefile to build kernel (with Make)."""

    if config["libs"]:
        if config["template"]:
            contents = TEMPLATE_BUILD_MAKEFILE.format(f"$(PWD)/workdir/apps/{config['template_name']}",
                                                      ":".join(f"$(UK_LIBS)/{l}" for l in config["libs"]))
        else:
            contents = TEMPLATE_BUILD_MAKEFILE.format("$(PWD)", ":".join(f"$(UK_LIBS)/{l}" for l in config["libs"]))
    else:
        contents = TEMPLATE_BUILD_MAKEFILE.format("$(PWD)", "")

    with open("Makefile", "w", encoding="utf-8") as stream:
        stream.write(contents)


def generate_build_make(config, t):
    """Generate build scripts using Make.

    Scripts are generated in scripts/build/ directory and start
    with the `make-` prefix.
    """

    if t['einitrd']:
        defconfig = f"{t['plat']}-{t['arch']}-einitrd"
        if config["docker"]:
            docker_export = TEMPLATE_RUN_DOCKER_EXPORT.format(config['name'], os.path.join(config["dockerdir"], DOCKER_MAKEFILE))
        else:
            docker_export = ""
        if config["template"]:
            initrd_base = f"$PWD/workdir/apps/{config['template_name']}"
        else:
            initrd_base = "."
        contents = TEMPLATE_BUILD_MAKE_EINITRD.format(docker_export, config['rootfs'], initrd_base, defconfig, f"{t['name']}_{t['plat']}-{t['arch']}")
    else:
        defconfig = f"{t['plat']}-{t['arch']}"
        contents = TEMPLATE_BUILD_MAKE.format(defconfig, f"{t['name']}_{t['plat']}-{t['arch']}")
    out_file = os.path.join(config["builddir"], f"make-{defconfig}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(contents)
    st = os.stat(out_file)
    os.chmod(out_file, st.st_mode | stat.S_IEXEC)


def generate_build_kraft(config, t):
    """Generate build scripts using Kraftkit.

    Scripts are generated in scripts/build/ directory and start
    with the `kraft-` prefix.
    """

    contents = TEMPLATE_BUILD_KRAFT.format(t['plat'], t['arch'],
                                           config['name'], t['plat'], t['arch'],
                                           config['name'], t['plat'], t['arch'])
    out_file = os.path.join(config["builddir"], f"kraft-{t['plat']}-{t['arch']}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(contents)
    st = os.stat(out_file)
    os.chmod(out_file, st.st_mode | stat.S_IEXEC)


def generate_build(config):
    """Generate build scripts.

    Scripts are generated in scripts/build/ directory.
    """

    shutil.copy(os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), DOCKER), DOCKER_MAKEFILE),
            os.path.join(config["dockerdir"], DOCKER_MAKEFILE))

    generate_build_makefile(config)

    # Generate make-based build scripts from targets.
    for t in config["targets"]:
        generate_build_make(config, t)

    # For kraft-based builds, only generated the einitrd variant.
    # The kernel name is defined by config["name"].
    for t in config["targets"]:
        if t["einitrd"] == True:
            generate_build_kraft(config, t)


def generate_run_fc_json(config, target, fs):
    """Generate running config (JSON) for Firecracker."""

    kernel = f"{target['name']}_{target['plat']}-{target['arch']}"

    if target["einitrd"]:
        json_name = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-einitrd-{fs}.json")
    else:
        json_name = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-{fs}.json")
    with open(json_name, "w", encoding="utf8") as stream:
        stream.write("{\n")
        stream.write('  "boot-source": {\n')
        stream.write(f'    "kernel_image_path": "{kernel}",\n')
        stream.write(f'    "boot_args": "{kernel} ')
        if config["networking"]:
            stream.write("netdev.ip=172.44.0.2/24:172.44.0.1::: ")
        if fs == "initrd":
            stream.write('vfs.fstab=[ \\"initrd0:/:extract::ramfs=1:\\" ] ')
        if config['cmd']:
            stream.write(f"-- {config['cmd']}\"")
        else:
            stream.write("-- template\"")
        if fs == "initrd":
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
        if config["networking"]:
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


def generate_run_fc(config, target, fs):
    """Generate running script using Firecracker."""

    if target["einitrd"]:
        header = TEMPLATE_RUN_FIRECRACKER_HEADER.format(os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-einitrd-{fs}.json"))
        out_file = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-einitrd-{fs}.sh")
    else:
        header = TEMPLATE_RUN_FIRECRACKER_HEADER.format(os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-{fs}.json"))
        out_file = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-{fs}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(header)
        stream.write(RUN_KILL_COMMANDS)
        if config["networking"]:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_FIRECRACKER_NET_COMMANDS)
        if fs == "initrd":
            if config['docker']:
                stream.write(TEMPLATE_RUN_DOCKER_EXPORT.format(f"{config['name']}", os.path.join(config["dockerdir"], DOCKER_MAKEFILE)))
            stream.write(TEMPLATE_RUN_CPIO_COMMANDS.format(f"{config['rootfs']}"))
        stream.write(RUN_FIRECRACKER_PREPARE)
        if config["networking"]:
            stream.write("sudo ")
        if target['arch'] == "x86_64":
            stream.write(RUN_FIRECRACKER_COMMAND.format("firecracker-x86_64"))
        else:
            stream.write(RUN_FIRECRACKER_COMMAND.format("firecracker-aarch64"))
        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run_qemu(config, target, fs):
    """Generate running script using QEMU."""

    kernel = f"{target['name']}_{target['plat']}-{target['arch']}"

    if config['cmd']:
        header = TEMPLATE_RUN_QEMU_HEADER.format(kernel, config["cmd"])
    else:
        header = TEMPLATE_RUN_QEMU_HEADER.format(kernel, "")

    if target["einitrd"]:
        out_file = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-einitrd-{fs}.sh")
    else:
        out_file = os.path.join(config["rundir"], f"{target['plat']}-{target['arch']}-{fs}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(header)
        stream.write(RUN_KILL_COMMANDS)
        if config["networking"]:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_QEMU_NET_COMMANDS)
        stream.write("\n")
        if fs == "initrd":
            if config['docker']:
                stream.write(TEMPLATE_RUN_DOCKER_EXPORT.format(f"{config['name']}", os.path.join(config["dockerdir"], DOCKER_MAKEFILE)))
            stream.write(TEMPLATE_RUN_CPIO_COMMANDS.format(f"{config['rootfs']}"))
        elif fs == "9pfs":
            if config['docker']:
                stream.write(TEMPLATE_RUN_DOCKER_EXPORT.format(f"{config['name']}", os.path.join(config["dockerdir"], DOCKER_MAKEFILE)))
            stream.write(TEMPLATE_RUN_9PFS_COMMANDS.format(f"{config['rootfs']}", f"{config['rootfs']}"))
        if config["networking"]:
            stream.write("sudo ")
        if target['arch'] == "x86_64":
            stream.write("qemu-system-x86_64 \\\n")
            if "accel" in config.keys():
                if config["accel"]:
                    stream.write("    -accel kvm \\\n")
        else:
            stream.write("qemu-system-aarch64 \\\n")
            stream.write("    -machine virt \\\n")
        stream.write('    -kernel "$kernel" \\\n')
        stream.write("    -nographic \\\n")
        stream.write(f"    -m {config['memory']}M \\\n")
        if config["networking"]:
            stream.write("    -netdev bridge,id=en0,br=virbr0 ")
            stream.write("-device virtio-net-pci,netdev=en0 \\\n")
            stream.write('    -append "netdev.ip=172.44.0.2/24:172.44.0.1::: ')
            if fs == "initrd":
                stream.write('vfs.fstab=[ \\"initrd0:/:extract::ramfs=1:\\" ] ')
            elif fs == "9pfs":
                stream.write('vfs.fstab=[ \\"fs0:/:9pfs:::\\" ] ')
            stream.write('-- $cmd" \\\n')
        else:
            stream.write('    -append "')
            if fs == "initrd":
                stream.write('vfs.fstab=[ \\"initrd0:/:extract::ramfs=1:\\" ] ')
            elif fs == "9pfs":
                stream.write('vfs.fstab=[ \\"fs0:/:9pfs:::\\" ] ')
            stream.write('-- $cmd" \\\n')
        if fs == "initrd":
            stream.write('    -initrd "$PWD"/initrd.cpio \\\n')
        elif fs == "9pfs":
            stream.write("    -fsdev local,id=myid,path=\"$rootfs\",security_model=none \\\n")
            stream.write("    -device virtio-9p-pci,fsdev=myid,mount_tag=fs0 \\\n")
        stream.write("    -cpu max\n")
        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run_kraft(config, target, fs):
    """Generate running script using KraftKit."""

    out_file = os.path.join(config["rundir"], f"kraft-{target['plat']}-{target['arch']}-{fs}.sh")
    with open(out_file, "w", encoding="utf8") as stream:
        stream.write(RUN_KRAFT_HEADER)
        stream.write(RUN_KILL_COMMANDS)
        if config["networking"]:
            stream.write(RUN_COMMON_NET_COMMANDS)
            stream.write(RUN_KRAFT_NET_COMMANDS)
        stream.write("\n")
        if config["networking"]:
            stream.write("sudo \\\n")
        stream.write("    KRAFTKIT_BUILDKIT_HOST=docker-container://buildkitd \\\n")
        stream.write("    KRAFTKIT_NO_WARN_SUDO=1 \\\n")
        stream.write("    kraft run \\\n")
        stream.write("    --log-level debug --log-type basic \\\n")

        if target['plat'] == "qemu":
            if "accel" not in config.keys():
                stream.write("    -W \\\n")
            elif not config["accel"]:
                stream.write("    -W \\\n")
            elif target['arch'] == 'arm64':
                stream.write("    -W \\\n")
        stream.write(f"    --memory {config['memory']}M \\\n")
        if config["networking"]:
            stream.write("    --network virbr0:172.44.0.2/24:172.44.0.1:::: \\\n")
        stream.write(f"    --arch {target['arch']} --plat {target['plat']}\n")

        stbuf = os.stat(out_file)
        os.chmod(out_file, stbuf.st_mode | stat.S_IEXEC)


def generate_run(config):
    """Generate running scripts."""

    for t in config["targets"]:
        if t['plat'] == "fc" or t['plat'] == "firecracker":
            if config["rootfs"] and t["einitrd"] == False:
                generate_run_fc_json(config, t, "initrd")
                generate_run_fc(config, t, "initrd")
            else:
                generate_run_fc_json(config, t, "nofs")
                generate_run_fc(config, t, "nofs")
        elif t['plat'] == "qemu":
            if config["rootfs"] and t["einitrd"] == False:
                generate_run_qemu(config, t, "initrd")
                generate_run_qemu(config, t, "9pfs")
            else:
                generate_run_qemu(config, t, "nofs")
        # For kraft-based runs, only consider the einitrd case.
        if t["einitrd"]:
            generate_run_kraft(config, t, "nofs")


def generate_test(config):
    """Generate testing scripts."""

    shutil.copy(os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "test"), "common.sh"),
            os.path.join(config["testdir"], "common.sh"))
    shutil.copy(os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "test"), "test.sh"),
            os.path.join(config["testdir"], "test.sh"))

    with open(os.path.join(config["testdir"], "config"), "w", encoding="utf8") as stream:
        stream.write("BUILD_SCRIPTS=\"\n")
        for entry in os.listdir(config["builddir"]):
            if entry.endswith(".sh"):
                stream.write(f"{entry}\n")
        stream.write("\"\n\n")
        stream.write("RUN_SCRIPTS=\"\n")
        for entry in os.listdir(config["rundir"]):
            if entry.endswith(".sh"):
                stream.write(f"{entry}\n")
        stream.write("\"\n\n")
        stream.write("SKIP_BUILD=0\n")
        stream.write("SKIP_RUN=0\n")


def main():
    """The main program function calls generate functions."""

    # Obtain configurations for running applications.
    try:
        with open(CONFIG, "r", encoding="utf8") as stream:
            config = yaml.safe_load(stream)
    except IOError:
        print(f"Error: Unable to open configuration file '{CONFIG}'", file=sys.stderr)
        sys.exit(1)

    if not "memory" in config.keys():
        print(f"Error: 'memory' attribute is not defined in '{CONFIG}'", file=sys.stderr)
        sys.exit(1)

    if not "networking" in config.keys():
        config["networking"] = None
    if not "scriptsdir" in config.keys():
        config["scriptsdir"] = SCRIPTS

    config["defconfigdir"] = os.path.join(config["scriptsdir"], DEFCONFIG)
    config["builddir"] = os.path.join(config["scriptsdir"], BUILD)
    config["rundir"] = os.path.join(config["scriptsdir"], RUN)
    config["testdir"] = os.path.join(config["scriptsdir"], TEST)
    config["dockerdir"] = os.path.join(config["scriptsdir"], DOCKER)

    if not os.path.exists(config["scriptsdir"]):
        os.mkdir(config["scriptsdir"])
    if not os.path.exists(config["defconfigdir"]):
        os.mkdir(config["defconfigdir"])
    if not os.path.exists(config["builddir"]):
        os.mkdir(config["builddir"])
    if not os.path.exists(config["rundir"]):
        os.mkdir(config["rundir"])
    if not os.path.exists(config["testdir"]):
        os.mkdir(config["testdir"])
    if not os.path.exists(config["dockerdir"]):
        os.mkdir(config["dockerdir"])

    try:
        with os.scandir(config["scriptsdir"]) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['scriptsdir']}'", file=sys.stderr)
    try:
        with os.scandir(config["defconfigdir"]) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['defconfigdir']}'", file=sys.stderr)
    try:
        with os.scandir(config["builddir"]) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['builddir']}'", file=sys.stderr)
    try:
        with os.scandir(config["rundir"]) as _:
            pass
    except IOError:
        print(f"Error: Unable to access running directory '{config['rundir']}'", file=sys.stderr)

    # Parse KraftKit config file (usually Kraftfile).
    try:
        with open(KRAFTCONFIG, "r", encoding="utf8") as stream:
            data = yaml.safe_load(stream)
    except IOError:
        print(f"Error: Unable to open Kraft configuration file '{KRAFTCONFIG}'", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print(f"Error: '{KRAFTCONFIG}' contents are not structured as a dictionary", file=sys.stderr)
        sys.exit(1)

    if "template" in data.keys():
        config["template"] = data["template"]["source"]
        config["template_name"] = config["template"].split("/")[-1].removeprefix("app-").removesuffix(".git")

    # Load configuration in config.
    if not "unikraft" in data.keys():
        print(f"Error: 'unikraft' attribute is not defined in '{KRAFTCONFIG}'", file=sys.stderr)
        sys.exit(1)
    config["kconfig"] = {}
    if isinstance(data["unikraft"], dict):
        if "kconfig" in data["unikraft"].keys():
            config["kconfig"] = data["unikraft"]["kconfig"]

    if not "name" in data.keys():
        pwd = os.path.basename(os.getcwd())
        print(f"'name' attribute is not defined in '{KRAFTCONFIG}'")
        print(f"Defaulting to directory name: '{pwd}'")
        config["name"] = pwd
    else:
        config["name"] = data["name"]

    if not "cmd" in data.keys():
        config['cmd'] = None
    else:
        config["cmd"] = " ".join(c for c in data["cmd"])

    config["docker"] = False
    if not "rootfs" in data.keys():
        config['rootfs'] = None
    else:
        config["rootfs"] = data["rootfs"]
        if os.path.basename(config["rootfs"]) == "Dockerfile":
            config["rootfs"] = "rootfs"
            config["docker"] = True

    einitrd = False
    if "CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD" in config["kconfig"].keys() and \
            config["kconfig"]["CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD"] == "y":
        einitrd = True
        config["kconfig"].pop("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD")
        config["kconfig"].pop("CONFIG_LIBVFSCORE_AUTOMOUNT_CI")

    if not "libraries" in data.keys():
        config["libs"] = None
    else:
        config["libs"] = list(data["libraries"].keys())
        for l in config["libs"]:
            if isinstance(data["libraries"][l], dict):
                if "kconfig" in data["libraries"][l].keys():
                    config["kconfig"].update(data["libraries"][l]["kconfig"])

    config["targets"] = []
    for t in data["targets"]:
        plat, arch = t.split('/')
        config["targets"].append({
            "plat": plat,
            "arch": arch,
            "einitrd": False,
            "name": config['name']})
        # If einitrd config is present, add a corresponding target.
        if einitrd == True:
            config["targets"].append({
                "plat": plat,
                "arch": arch,
                "einitrd": True,
                "name": f"{config['name']}-einitrd"})

    generate_setup(config)
    generate_defconfig(config)
    generate_build(config)
    generate_run(config)
    generate_test(config)


if __name__ == "__main__":
    sys.exit(main())
