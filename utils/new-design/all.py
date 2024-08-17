import os
import yaml
import itertools
import platform
import subprocess
import re
import shutil
import sys

class TesterConfig:
    """Store tester configuration.

    Configuration is read from the global tester configuration file.
    """

    def __init__(self, config_file):
        try:
            with open(config_file, "r", encoding="utf8") as stream:
                self.config = yaml.safe_load(stream)
        except IOError:
            print(f"Error: Unable to open configuration file '{config_file}'", file=sys.stderr)
            return None

    def generate_variants(self):
        variants = self.config['variants']
        return (dict(zip(variants.keys(), values)) for values in itertools.product(*variants.values()))

    def generate_compilers(self, plat, arch, system_comp):
        compilers = []
        for c in self.config['tools']['compiler']:
            if c.key == "system":
                compilers.append(system_comp)
                continue
            if c['arch'] == arch:
                compilers.append({
                    "type": c['type'],
                    "path": c['path']
                    })
        return compilers

    def generate_vmms(self, plat, arch, system_vmm):
        vmms = []
        for v in self.config['tools']['vmm']:
            if v.key == "system":
                vmms.append(system_comp)
                continue
            if v['arch'] == arch and v['type'] == plat:
                vmms.append({
                    "platform": v['type'],
                    "path": v['path']
                    })
        return vmms


    def get_valid_configs(plat, arch, vmm, comp, build_tool, run_tool):
        valid_configs = []
        for v in self.generate_variants():
            if plat == v['platform'] and \
                    arch == v['arch'] and \
                    build_tool == v['build_tool'] and \
                    run_tool == v['run_tool']:
                _config = v
                _config.update['base'] = self.config['source']['base']
                for _comp in self.generate_compilers(self, comp):
                    _config.update['compiler'] = _comp
                    for _vmm in self.generate_vmms(self, vmm):
                        _config.update['vmm'] = _vmm
                        valid_configs.append(_config)

        return valid_configs

    def __str__(self):
        return str(self.config)


class SystemConfig:
    """Extract system configuration information.
    Store in appropriate class members.

    self.os: operating system / platform info
    self.arch: CPU architecture
    self.hypervisor: hypervisor / acceleration
    self.vmms: virtual machine monitor paths (split by architecture and type)
    self.compilers: compiler paths (split by architecture and type)
    """

    def _get_os(self):
        info = platform.uname()
        self.os = {
                "type": info.system,
                "kernel_version": info.release,
                "distro": None
                }
        if self.os["type"] == "Linux":
            self.os["distro"] = platform.freedesktop_os_release()["ID"]

    def _get_arch(self):
        self.arch = platform.machine()

    def _get_hypervisor(self):
        self.hypervisor = ""
        if self.os["type"] == "Linux":
            with subprocess.Popen("lsmod", stdout=subprocess.PIPE) as proc:
                content = proc.stdout.read()
                if re.search(b"\\nkvm", content):
                    self.hypervisor = "kvm"

    def _get_paths(self, string, pattern):
        cmds = []
        with subprocess.Popen(["bash", "-c", f"compgen -A command {string}"], stdout=subprocess.PIPE) as proc:
            for l in proc.stdout.readlines():
                l = l.decode('utf-8').strip()
                if re.match(pattern, l):
                    cmds.append(l)

        cmds = set(cmds)
        paths = []
        for c in cmds:
            if shutil.which(c):
                paths.append(shutil.which(c))

        return paths

    def _get_vmms(self):
        qemu_x86_64_paths = self._get_paths("qemu-system-", "^qemu-system-x86_64$")
        firecracker_x86_64_paths = self._get_paths("qemu-system-", "^qemu-system-aarch64")
        qemu_arm64_paths = self._get_paths("firecracker-", "^firecracker-x86_64")
        firecracker_arm64_paths = self._get_paths("firecracker-", "^firecracker-aarch64")
        self.vmms = {
                'arm64': {
                    'qemu': qemu_arm64_paths,
                    'firecracker': firecracker_arm64_paths
                    },
                'x86_64': {
                    'qemu': qemu_x86_64_paths,
                    'firecracker': firecracker_x86_64_paths
                    }
                }

    def _get_compilers(self):
        gcc_x86_64_paths = self._get_paths("gcc-", "^gcc-[0-9]+$")
        gcc_arm64_paths = self._get_paths("aarch64-linux-gnu-gcc-", "aarch64-linux-gnu-gcc-[0-9]+$")
        clang_paths = self._get_paths("clang-", "^clang-[0-9]+$")
        self.compilers = {
                'arm64': {
                    'gcc': gcc_arm64_paths,
                    'clang': clang_paths
                    },
                'x86_64': {
                    'gcc': gcc_x86_64_paths,
                    'clang': clang_paths
                    }
                }

    def __init__(self):
        self._get_os()
        self._get_arch()
        self._get_hypervisor()
        self._get_vmms()
        self._get_compilers()

    def __str__(self):
        vmm_list = self.vmms["arm64"]["qemu"]
        vmm_list.extend(self.vmms["arm64"]["firecracker"])
        vmm_list.extend(self.vmms["x86_64"]["qemu"])
        vmm_list.extend(self.vmms["x86_64"]["firecracker"])
        vmm_str = ", ".join(vmm for vmm in vmm_list)

        comp_list = self.compilers["arm64"]["gcc"]
        comp_list.extend(self.compilers["arm64"]["clang"])
        comp_list.extend(self.compilers["x86_64"]["gcc"])
        comp_list.extend(self.compilers["x86_64"]["clang"])
        comp_str = ", ".join(comp for comp in comp_list)

        return f'os: {self.os["type"]}, kernel: {self.os["kernel_version"]}, ' \
                f'distro: {self.os["distro"]}, arch: {self.arch}, ' \
                f'hypervisor: {self.hypervisor}, vmms: {vmm_str}, ' \
                f'compilers: {comp_str}'


class AppConfig:
    """Store application configuration.

    Configuration is read from the application configuration file (typically
    `Kraftfile`) and the user configuration file (typically `config.yaml`).
    """

    def has_template(self):
        if "template" in self.app_config.keys():
            return True
        return False

    def is_runtime(self):
        if "unikraft" in self.app_config.keys():
            return True
        return False

    def is_example(self):
        return not self.is_runtime()

    def is_bincompat(self):
        return self.has_template(self)

    def _parse_user_config(self, user_config_file):
        with open(user_config_file, "r", encoding="utf-8") as stream:
            self.user_config = yaml.safe_load(stream)

    def _parse_app_config(self, app_config_file):
        with open(app_config_file, "r", encoding="utf-8") as stream:
            self.app_config = yaml.safe_load(stream)

    def __init__(self, app_config="Kraftfile", user_config="config.yaml"):
        self._parse_user_config(user_config)
        self._parse_app_config(app_config)

    def __str__(self):
        return str(self.app_config) + "\n" + str(self.user_config)


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

    def generate(self):
        # Create directory.
        # Generate config.yaml.
        self.build_config.generate()
        self.run_config.generate()
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

    def generate(self):
        # Generate build.sh script.
        # Optionally, generate defconfig file.
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

    def generate(self):
        # Generate run.sh script.
        pass


class TestRunner:
    pass


def generate_target_configs(tester_config, app_config, system_config):
    for (plat, arch) in app_config.get_targets():
        for vmm in system_config.get_vmms(plat, arch):
            for comp in system_config.get_comps(arch):
                for build_tool in BuildConfig.get_build_tools(plat, arch):
                    for run_tool in RunConfig.get_run_tools(plat, arch):
                        for config in tester_config.get_valid_configs(plat, arch, vmm, comp, build_tool, run_tool):
                            t = TargetConfig(config, app_config, system_config)


t = TesterConfig("../../../utils/new-design/tester.yaml")
print(t)
a = AppConfig()
print(a)
s = SystemConfig()
print(s)

#targets = generate_target_configs(t, a, s)
#for t in targets:
#    t.generate()
