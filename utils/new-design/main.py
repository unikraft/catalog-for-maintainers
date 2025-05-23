import os
import sys
import distutils
import TesterConfig
import SystemConfig
import AppConfig
import TargetSetup
import BuildSetup
import RunSetup


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def copy_common():
    """Copy all common scripts to the test directory.

    These scripts are to be used in the build, run and test phases.
    """

    base = os.path.abspath('.tests')
    dest = os.path.join(base, "common")
    src = os.path.join(SCRIPT_DIR, "common")
    distutils.dir_util.copy_tree(src, dest, update=1)


def generate_target_configs(tester_config, app_config, system_config):
    """Generate all possible target configurations for given application on given system.

    A target configuration will generate the corresponding build configuration and
    run configurations.

    Return list of all target configurations in `targets` variable.
    """

    for (plat, arch) in app_config.config['targets']:
        vmms = system_config.get_vmms(plat, arch)
        compilers = system_config.get_compilers(plat, arch)
        build_tools = BuildSetup.BuildSetup.get_build_tools(plat, arch)
        run_tools = RunSetup.RunSetup.get_run_tools(plat, arch)
        tester_config.generate_target_configs(plat, arch, system_config.get_arch(), vmms, compilers, build_tools, run_tools)

    targets = []
    for config in tester_config.get_target_configs():
        t = TargetSetup.TargetSetup(config, app_config, system_config)
        targets.append(t)

    return targets


def usage(argv0):
    print(f"Usage: {argv0} <path/to/tester.yaml>", file=sys.stderr)


def main():
    if (len(sys.argv) != 2):
        usage(sys.argv[0])
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print(f"Not a file: {sys.argv[1]}")
        sys.exit(1)

    t = TesterConfig.TesterConfig(sys.argv[1])
    a = AppConfig.AppConfig()
    a.generate_init(t)
    s = SystemConfig.SystemConfig()

    copy_common()

    targets = generate_target_configs(t, a, s)
    for t in targets:
        t.generate()

if __name__ == "__main__":
    sys.exit(main())
