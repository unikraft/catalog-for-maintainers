import os
import yaml
import itertools
import platform
import subprocess
import re
import shutil
import sys
import string

SCRIPT_DIR = "."

class TesterConfig:
    """Interact with tester configuration.

    Configuration is read from the global tester configuration file.
    Extract valid configurations from tester configuration file.

    Provide configurations for target definition: get_target_configs()
    """

    def __init__(self, config_file):
        try:
            with open(config_file, "r", encoding="utf8") as stream:
                self.config = yaml.safe_load(stream)
                self.variants = self._generate_variants()
        except IOError:
            print(f"Error: Unable to open configuration file '{config_file}'", file=sys.stderr)
            return None

    def _generate_full_variants(self):
        """Generate all possible configuration variants.

        Create all combinations of values from the 'variants' dictionary in
        the tester configuration file.

        Each variant is a dictionary, e.g.
        {'arch': 'x86_64', 'hypervisor': 'kvm', 'platform': 'qemu', ...}

        Return a list of all variants.
        """

        variants = self.config['variants']
        return list(dict(zip(variants.keys(), values)) for values in itertools.product(*variants.values()))

    def _get_exclude_variants(self):
        """Get variants to be excluded from all possible variants.

        Parse values in the 'exclude_variants' list in the tester
        configuration file.

        Each exclude variant is a dictionary with various keys, e.g:
        {'networking': 'brigde', 'platform': 'firecracker'}
        """

        variants = self.config['variants']
        exclude_variants = self.config['exclude_variants']
        ret = []

        for e in exclude_variants:
            tmp_dict = {}
            for k1, v1 in e.items():
                if isinstance(v1, list):
                    l = list(variants[k1])
                    for v2 in v1:
                        if v2.startswith("not"):
                            tmp_l = list(set(variants[k1]) - set([v2.split(" ")[1]]))
                        else:
                            tmp_l = [v2]
                        l = set.intersection(set(l), set(tmp_l))
                    tmp_dict[k1] = l
                elif isinstance(v1, str):
                    if v1.startswith("not"):
                        l = list(set(variants[k1]) - set([v1.split(" ")[1]]))
                    else:
                        l = [v1]
                    tmp_dict[k1] = l
                else:
                    l = [v1]
                    tmp_dict[k1] = l
            ret.extend(list(dict(zip(tmp_dict, x)) for x in itertools.product(*tmp_dict.values())))

        return ret

    def _generate_variants(self):
        """Generate valid variants.

        Valid variants are those that are not excluded. In short, do a diff
        between all variants (with _generate_full_variants()) and the excluded
        variants (with _get_exlude_variants()).

        An exclude variant is a dictionary. A variant is a dictionary. If all
        items in the exclude variant ar part of the variant, that variant is
        not used.

        Return list of variants, i.e. a sublist of the full variants.
        """

        exclude_variants = self._get_exclude_variants()
        full_variants = self._generate_full_variants()
        ret_variants = []

        for f in full_variants:
            excluded = True
            for e in exclude_variants:
                excluded = True
                for k, v in e.items():
                    if f[k] != v:
                        excluded = False
                        break
                if excluded:
                    break
            if not excluded:
                 ret_variants.append(f)

        return ret_variants

    def _generate_compilers(self, plat, arch, system_comp):
        """Generate compiler configurations.

        Generate compiler configurations using system compiler configuration
        and tester configuration for the specific architecture. The platform
        is also passed as argument for potential future use.

        Return list of compiler configurations. Each item in the list is
        a dictionary, e.g.:
        {'type': 'gcc', 'path': '/usr/bin/gcc'}
        """

        compilers = []

        for c in self.config['tools']['compiler']:
            if isinstance(c, dict):
                if c['arch'] == arch:
                    compilers.append({
                        "type": c['type'],
                        "path": c['path']
                        })
                continue
            if c == "system":
                compilers.append(system_comp)

        return compilers

    def _generate_vmms(self, plat, arch, system_vmm):
        """Generate VMM configurations.

        Generate VMM configurations using system VMM configuration and tester
        configuration for the specific platform and architecture.

        Return list of compiler configurations. Each item in the list is
        a dictionary, e.g.:
        {'platform': 'qemu', 'path': '/usr/bin/qemu-system-x86_64'}
        """

        vmms = []

        for v in self.config['tools']['vmm']:
            if isinstance(v, dict):
                if v['arch'] == arch and v['type'] == plat:
                    vmms.append({
                        "platform": v['type'],
                        "path": v['path']
                        })
                continue
            if v == "system":
                vmms.append(system_vmm)

        return vmms

    def get_target_configs(self, plat, arch, vmm, comp, build_tool, run_tool):
        """Get configurations for target.

        The target is defined by the platform, architecture, system VMMs,
        system compiler, build tools and run tools. Do an intersection between
        the valid_variants list and the target specification.

        Return list of target configurations. Each item in the list is a
        dictionary, e.g.:
        {'arch': 'x86_64', ..., 'base': '...', 'compiler': '...' }'
        """

        target_configs = []

        for v in self.variants:
            if plat == v['platform'] and \
                    arch == v['arch'] and \
                    build_tool == v['build_tool'] and \
                    run_tool == v['run_tool']:
                _config = v
                _config['base'] = self.config['source']['base']
                for _comp in self._generate_compilers(plat, arch, comp):
                    _config['compiler'] = _comp
                    for _vmm in self._generate_vmms(plat, arch, vmm):
                        _config['vmm'] = _vmm
                        target_configs.append(_config)

        return target_configs

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
        """Get operating system information.

        Store in the self.of dictionary.
        """

        info = platform.uname()
        self.os = {
                "type": info.system,
                "kernel_version": info.release,
                "distro": None
                }
        if self.os["type"] == "Linux":
            self.os["distro"] = platform.freedesktop_os_release()["ID"]

    def _get_arch(self):
        """Get machine architecture information.

        Store in the self.arch string.
        """

        self.arch = platform.machine()

    def _get_hypervisor(self):
        """Get hypervisor information.

        Store in the self.hypervisor string.
        """

        self.hypervisor = ""
        if self.os["type"] == "Linux":
            with subprocess.Popen("lsmod", stdout=subprocess.PIPE) as proc:
                content = proc.stdout.read()
                if re.search(b"\\nkvm", content):
                    self.hypervisor = "kvm"

    def _get_paths(self, string, pattern):
        """Get full paths for string (part of a command).

        Use Bash completion to expand string to a full command. Match result
        against pattern. Only select results that match.
        Use `which` to get the absolute path for the full command.

        Return list of full paths.

        TODO: This has only been tested on Bash.
        Test on other shells.
        """

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
        """Get VMMs information.

        Store in the self.vmms dictionary.
        """

        qemu_x86_64_paths = self._get_paths("qemu-system-", "^qemu-system-x86_64$")
        qemu_arm64_paths = self._get_paths("qemu-system-", "^qemu-system-aarch64")
        firecracker_x86_64_paths = self._get_paths("firecracker-", "^firecracker-x86_64")
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
        """Get compilers information.

        Store in the self.compilers dictionary.
        """

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

    def get_vmms(self, plat, arch):
        """Get available VMMs for platform and architecture.

        Return list of dictionaries of available VMMs.
        """

        ret_list = []
        for v in self.vmms[arch][plat]:
            ret_list.append({
                "type": plat,
                "path": v
                })
        return ret_list

    def get_compilers(self, plat, arch):
        """Get available compilers for platform and architecture.

        The platform is not used; it is passed as a parameter for future use.

        Return list of dictionaries of available compilers.
        """

        ret_list = []
        for k, v in self.compilers[arch].items():
            for l in v:
                ret_list.append({
                    "type": k,
                    "path": l
                    })
        return ret_list

    def __init__(self):
        """Initialize object.

        Extract all system information: operating system, architecture,
        hypervisor, VMMs, compilers.
        """

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
        return self.config['template'] != None

    def has_einitrd(self):
        return self.einitrd

    def is_runtime(self):
        return self.is_kernel()

    def is_kernel(self):
        return bool(self.config['unikraft'])

    def is_example(self):
        return not self.is_runtime()

    def is_bincompat(self):
        return self.has_template()

    def _parse_user_config(self, user_config_file):
        with open(user_config_file, "r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)

        self.config["networking"] = False

        if not "networking" in data.keys():
            self.config["networking"] = False
        else:
            self.config["networking"] = data["networking"]

        if not "test_dir" in data.keys():
            self.config["test_dir"] = None
        else:
            self.config["test_dir"] = data["test_dir"]

        if not "memory" in data.keys():
            print(f"Error: 'memory' attribute is not defined in {user_config_file}'", file=sys.stderr)
            sys.exit(1)
        else:
            self.config["memory"] = data["memory"]

    def _parse_app_config(self, app_config_file):
        with open(app_config_file, "r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)

        self.config["unikraft"] = {}
        if "unikraft" in data.keys():
            if isinstance(data["unikraft"], dict):
                if "kconfig" in data["unikraft"].keys():
                    self.config["unikraft"]["kconfig"] = data["unikraft"]["kconfig"]
                    self.einitrd = False
                    if "CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD" in self.config["unikraft"]["kconfig"].keys() and \
                            self.config["unikraft"]["kconfig"]["CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD"] == "y":
                        self.einitrd = True
                        self.config["unikraft"]["kconfig"].pop("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD")
                        self.config["unikraft"]["kconfig"].pop("CONFIG_LIBVFSCORE_AUTOMOUNT_CI")


        if not "template" in data.keys():
            self.config["template"] = None
        else:
            self.config["template"] = self.data["template"].split("/")[-1]
            if self.config["template"].endswith(".git"):
                self.config["template"] = self.config["template"][:-4]

        if not "name" in data.keys():
            self.config["name"] = os.path.basename(os.getcwd())
        else:
            self.config["name"] = data["name"]

        if not "runtime" in data.keys():
            self.config["runtime"] = None
        else:
            self.config["runtime"] = data["runtime"]

        if not 'targets' in data.keys():
            self.config['targets'] = None
        else:
            targets = []
            for t in data['targets']:
                plat = t.split("/")[0]
                arch = t.split("/")[1]
                if plat == "fc":
                    plat = "firecracker"
                targets.append((plat, arch))
            self.config['targets'] = targets

        if not "cmd" in data.keys():
            self.config['cmd'] = None
        else:
            self.config["cmd"] = " ".join(c for c in data["cmd"])

        if not "rootfs" in data.keys():
            self.config['rootfs'] = None
        else:
            self.config["rootfs"] = data["rootfs"]

        self.config["libraries"] = {}
        if "libraries" in data.keys():
            for l in data["libraries"].keys():
                self.config["libraries"][l] = {}
                self.config["libraries"][l]["kconfig"] = {}
                if isinstance(data["libraries"][l], dict):
                    if "kconfig" in data["libraries"][l].keys():
                        self.config["libraries"][l]["kconfig"] = data["libraries"][l]["kconfig"]

    def __init__(self, app_config="Kraftfile", user_config="config.yaml"):
        self.config = {}
        self._parse_user_config(user_config)
        self._parse_app_config(app_config)

    def __str__(self):
        return str(self.config) + "\n" + str(self.user_config)


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
    class_id = 1

    def __init__(self, config, app_config, system_config):
        self.config = config
        self.id = TargetConfig.class_id
        TargetConfig.class_id += 1
        if app_config.config['test_dir']:
            base = os.path.abspath(app_config.user_config['test_dir'])
        else:
            base = os.path.abspath('.tests')
        self.dir = os.path.join(base, "{:05d}".format(self.id))
        self.build_config = BuildConfig(self.dir, self.config, app_config)
        self.run_config = RunConfig(self.dir, self.config, app_config)

    def generate(self):
        # Create directory.
        os.mkdir(self.dir, mode=0o755)
        # Generate config.yaml.
        with open(os.path.join(self.dir, 'config.yaml'), 'w') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False)
        self.build_config.generate()
        self.run_config.generate()


class BuildConfig:
    BUILD_TOOL_NONE = None
    build_tool = {
            'type': BUILD_TOOL_NONE,
            'recipe': None
            }
    build_script = None
    build_dir = None
    artifacts_dir = None

    def __init__(self, base_dir, target_config, app_config):
        self.dir = base_dir
        self.target_config = target_config
        self.app_config = app_config

    def get_build_tools(plat, arch):
        return ["make", "kraft"]

    def _generate_defconfig(self):
        """Generate default configuration file for Make-based build."""

        with open(os.path.join(self.dir, "defconfig"), "w", encoding="utf-8") as stream:
            stream.write(f"CONFIG_UK_NAME=\"{self.app_config.config['name']}\"\n")
            stream.write(f"CONFIG_UK_DEFNAME=\"{self.app_config.config['name']}\"\n")
            if self.app_config.has_einitrd():
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD=y\n")
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI=y\n")
            else:
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD=n\n")
                stream.write("CONFIG_LIBVFSCORE_AUTOMOUNT_CI=n\n")
            if self.target_config['platform'] == 'qemu':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_QEMU=y\n")
            if self.target_config['platform'] == 'firecracker':
                stream.write("CONFIG_PLAT_KVM=y\n")
                stream.write("CONFIG_KVM_VMM_FIRECRACKER=y\n")
            if self.target_config['arch'] == 'arm64':
                stream.write("CONFIG_ARCH_ARM_64=y\n")
            if self.target_config['arch'] == 'x86_64':
                stream.write("CONFIG_ARCH_X86_64=y\n")
            if self.app_config.config["unikraft"]:
                for k, v in self.app_config.config["unikraft"]["kconfig"].items():
                    stream.write(f"{k}={v}\n")
            if 'libraries' in self.app_config.config.keys():
                for l in self.app_config.config["libraries"].keys():
                    if l.startswith("lib"):
                        stream.write("CONFIG_{}=y\n".format(l.replace('-', '_').upper()))
                    else:
                        stream.write("CONFIG_LIB{}=y\n".format(l.replace('-', '_').upper()))
                    for k, v in self.app_config.config["libraries"][l]["kconfig"].items():
                        stream.write(f"{k}={v}\n")

    def _generate_makefile(self):
        """Generate Makefile for Make-based build."""

        with open(os.path.join(SCRIPT_DIR, "tpl_Makefile"), "r", encoding="utf-8") as stream:
            raw_content = stream.read()

        if self.app_config.has_template():
            app_dir = os.path.join(os.path.join(self.target_config["base"], "apps"), self.app_config.config['template'])
        else:
            app_dir="$(PWD)"
        libs = ""
        if 'libraries' in self.app_config.config.keys():
            for l in self.app_config.config["libraries"].keys():
                libs += f"$(LIBS_BASE)/{l}:"
            libs = libs[:-1]
        base = self.target_config["base"]
        target_dir = self.dir

        content = raw_content.format(**locals())

        with open(os.path.join(self.dir, "Makefile"), "w", encoding="utf-8") as stream:
            stream.write(content)

    def _generate_kraftfile(self):
        """Generate Kraftfile for Kraft-based build.

        The generated Kraftfile is more-ore-less a copy of the initial Kraftfile.
        Custom einitrd configuration, debug levels configuration is added.
        """

        with open(os.path.join(self.dir, "Kraftfile"), "w", encoding="utf-8") as stream:
            stream.write("spec: v0.6\n\n")

            stream.write(f"name: {self.app_config.config['name']}\n\n")

            if self.app_config.config['runtime']:
                stream.write(f"runtime: {self.app_config.config['runtime']}\n\n")

            if self.app_config.config['rootfs']:
                stream.write(f"rootfs: {self.app_config.config['rootfs']}\n\n")

            if self.app_config.config['cmd']:
                stream.write(f"cmd: \"{self.app_config.config['cmd']}\"\n\n")

            if self.app_config.config['template']:
                template_path = os.path.join(os.path.join(self.target_config["base"], "apps"), self.app_config.config['template'])
                stream.write("template:\n")
                stream.write(f"  source: {template_path}\n\n")

            stream.write("targets:\n")
            stream.write(f"- {self.target_config['platform']}/{self.target_config['arch']}\n\n")

            if self.app_config.config['unikraft']:
                unikraft_path = os.path.join(self.target_config["base"], "unikraft")
                stream.write("unikraft:\n")
                stream.write(f"  source: {unikraft_path}\n")
                if self.app_config.config['unikraft']['kconfig']:
                    stream.write("  kconfig:\n")
                    for k,v in self.app_config.config['unikraft']['kconfig'].items():
                        if isinstance(v, str):
                            v = f"\"{v}\""
                        stream.write(f"    {k}: {v}\n")
                    if self.app_config.has_einitrd():
                        stream.write("    CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD: 'y'\n")
                        stream.write("    CONFIG_LIBVFSCORE_AUTOMOUNT_CI: 'y'\n")
                    else:
                        stream.write("    CONFIG_LIBVFSCORE_AUTOMOUNT_CI_EINITRD: 'n'\n")
                        stream.write("    CONFIG_LIBVFSCORE_AUTOMOUNT_CI: 'n'\n")
                    stream.write("\n")
                stream.write("\n")

            if 'libraries' in self.app_config.config.keys():
                stream.write("libraries:\n")
                for l in self.app_config.config["libraries"].keys():
                    lib_path = os.path.join(os.path.join(self.target_config["base"], "libs"), l)
                    stream.write(f"  {l}:\n")
                    stream.write(f"    source: {lib_path}\n")
                    if self.app_config.config["libraries"][l]["kconfig"]:
                        stream.write(f"    kconfig:\n")
                        for k, v in self.app_config.config["libraries"][l]["kconfig"].items():
                            if isinstance(v, str):
                                v = f"\"{v}\""
                            stream.write(f"      {k}: {v}\n")

    def generate(self):
        # Generate build.sh script.
        # Optionally, generate defconfig file.
        if self.target_config['build_tool'] == 'make':
            self._generate_defconfig()
            if self.app_config.is_kernel():
                self._generate_makefile()
        elif self.target_config['build_tool'] == 'kraft':
            self._generate_kraftfile()


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

    def __init__(self, base_dir, target_config, app_config):
        self.dir = base_dir
        self.target_config = target_config
        self.app_config = app_config

    def get_run_tools(plat, arch):
        return ["vmm", "kraft"]

    def generate(self):
        # Generate run.sh script.
        pass


class TestRunner:
    pass


def generate_target_configs(tester_config, app_config, system_config):
    targets = []
    for (plat, arch) in app_config.config['targets']:
        for vmm in system_config.get_vmms(plat, arch):
            for comp in system_config.get_compilers(plat, arch):
                for build_tool in BuildConfig.get_build_tools(plat, arch):
                    for run_tool in RunConfig.get_run_tools(plat, arch):
                        for config in tester_config.get_target_configs(plat, arch, vmm, comp, build_tool, run_tool):
                            t = TargetConfig(config, app_config, system_config)
                            targets.append(t)
    return targets

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

t = TesterConfig("../../../utils/new-design/tester.yaml")
a = AppConfig()
s = SystemConfig()

targets = generate_target_configs(t, a, s)
for t in targets:
    t.generate()
