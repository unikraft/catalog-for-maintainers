import os
import yaml
import itertools

class ConfigVariants:
    arch = ['arm64', 'x86_64']
    hypervisor = ['none', 'kvm', 'xen']
    platform = ['qemu', 'firecracker', 'xen']
    build_tool = ['make', 'kraft']
    run_tool = ['vmm', 'kraft']
    bootloader = ['multiboot', 'uefi']
    pie = [False, True]
    debug = ['none', 'strace', 'err', 'info', 'debug']
    fs = ['none', 'initrd', '9pfs']
    networking = ['none', 'bridge', 'nat', 'tap']

    def _convert_to_dict(i):
        return {
                'arch': i[0],
                'hypervisor': i[1],
                'platform': i[2],
                'build_tool': i[3],
                'run_tool': i[4],
                'bootloader': i[5],
                'debug': i[6],
                'fs': i[7],
                'networking': i[8]
                }

    def _is_valid_config(d):
        if d['networking'] == 'bridge' and d['platform'] == 'firecracker':
            return False
        if d['networking'] == 'tap' and d['platform'] != 'firecracker':
            return False
        if d['bootloader'] == 'uefi' and d['arch'] != 'x86_64':
            return False
        if d['platform'] == 'firecracker' and d['hypervisor'] != 'kvm':
            return False
        if d['platform'] == 'xen' and d['hypervisor'] != 'xen':
            return False
        if d['platform'] == 'qemu' and (d['hypervisor'] != 'kvm' and d['hypervisor'] != 'none'):
            return False
        if d['fs'] == '9pfs' and d['platform'] == 'firecracker':
            return False
        return True

    def generate_config_variants(self):
        variants = []
        for i in itertools.product(self.arch, self.hypervisor, self.platform,
                                   self.build_tool, self.run_tool,
                                   self.bootloader, self.debug, self.fs,
                                   self.networking):
            d = ConfigVariants._convert_to_dict(i)
            if ConfigVariants._is_valid_config(d):
                variants.append(d)
        return variants

class SystemConfig:
    OS_TYPE_NONE = None
    ARCH_NONE = None
    HYPERVISOR_NONE = None
    os = {
            "type": OS_TYPE_NONE,
            "kernel_version": None,
            "distro": None
            }
    arch = ARCH_NONE
    hypervisor = HYPERVISOR_NONE
    vmms = {
            'arm64': [],
            'x86_64': []
            }
    compilers = {
            'arm64': [],
            'x86_64': []
            }

    def _get_os(self):
        pass

    def _get_arch(self):
        pass

    def _get_hypervisor(self):
        pass

    def _get_vmms(self):
        pass

    def _get_compilers(self):
        pass

    def __init__(self):
        _get_os()
        _get_arch()
        _get_hypervisor()
        _get_vmms()
        _get_compilers()


class AppConfig:
    ROOTFS_PATH_TYPE_NONE = None
    SOURCES_TYPE_NONE = None
    memory = 8
    networking_enabled = False
#    accel_enabled = False
    specification = None
    name = None
    cmd = None
    ROOTFS_PATH_TYPE_NONE = None
    rootfs = {
            'path': None,
            'path_type': ROOTFS_PATH_TYPE_NONE
            }
    template = None
    kernel = {
            'version': None,
            'source': None,
            'config': {}
            }
    libs = []
    targets = []
    scripts_dir = os.path.join(os.getcwd(), "scripts")
    sources = {
            'type': SOURCES_TYPE_NONE,
            'path': None
            }
    target_configs = []

    def _parse_user_config(self):
        pass

    def _parse_app_config(self):
        pass

    def __init__(self, user_config="config.yaml"):
        _parse_user_config()
        _parse_app_config()

    def generate_target_configs(self):
        for t in self.targets:
            pass

class TargetConfig:
    PLATFORM_NONE = None
    ARCH_NONE = None
    BOOTLOADER_TYPE_NONE = None
    DEBUG_NONE = None
    platform = PLATFORM_NONE
    arch = ARCH_NONE
    pie_enabled = False
    paging_enabled = False
    bootloader = BOOTLOADER_TYPE_NONE
    debug = DEBUG_NONE
    compiler = None
    embedded_initrd = False

    def __init__(self):
        pass

class BuildConfig:
    BUILD_TOOL_NONE = None
    build_tool = {
            'type': BUILD_TOOL_NONE,
            'recipe': None
            }
    build_script = None
    build_dir = None
    artifacts_dir = None

    def __init__(self):
        pass

class RunConfig:
    NET_TYPE_NONE = None
    RUN_TOOL_NONE = None
    FS_TYPE_NONE = None
    net_type = NET_TYPE_NONE
    run_tool = {
            'type': RUN_TOOL_NONE,
            'config': None
            }
    fs_type = FS_TYPE_NONE
    run_script = None

    def __init__(self):
        pass

class TestRunner:
    pass

c = ConfigVariants()
for i in c.generate_config_variants():
    print(i)
