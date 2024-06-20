# Catalog for Maintainers

> [!WARNING]
> This repository is used by the Unikraft Open-Source Project maintainers.
>
> For the general-purpose Community Catalog, please visit:
> https://github.com/unikraft/catalog

These are common instructions for applications in the extended maintainers catalog.
Each application gets their own directory, used for documenting, setting up, configuring, building, running, testing and debugging the application.
Common information, configuration scripts are collected together in other directories such as `utils/`.

Instructions below assume you are running commands in the application directory.

## Application Directory Contents

A typical directory for an application contains:

* `Kraftfile`: build / run rules, including pulling the `base` image
* `Dockerfile` (optional): filesystem specification, including binary and libraries
* `Makefile.docker` (optional): used to generate the root filesystem from the `Dockerfile` rules
* `README.md`: specific application instructions, such as starting and testing an application
* `config.yaml`: configuration file to generate script files to run the application
* `single_test.sh`: basic application test
* specific application files, such as configuration files and source code files, typically part of the `rootfs/` directory

## Common Setup

The following are required before building and running an app.
In case you have already done them for other application runs, you can skip them:

1. [Install Unikraft's companion command-line toolchain `kraft`](https://unikraft.org/docs/cli).

1. Configure `kraft` to be able to pull contents from GitHub.
   For this, first [generate a GitHub token](https://github.com/settings/tokens/new) that has all the `repo` list items checked.
   Configure `kraft` to use the token:

   ```console
   kraft login -u <username> -t <token> github.com
   ```

   In the command above, replace `<username>` with your GitHub username and `<token>` with the generated token.

1. Install Docker following the [official instructions](https://docs.docker.com/engine/install/).
   This can be either [Docker Engine](https://docs.docker.com/engine/) or [Docker Desktop](https://docs.docker.com/desktop/).

1. Start a [BuildKit](https://docs.docker.com/build/buildkit/) container to be used by KraftKit to build the filesystem from the `Dockerfile`.
   While in the top-level directory of this repository, source the `utils/start-buildkit.sh` directory:

   ```console
   source utils/start-buildkit.sh
   ```

## Basic Build, Run and Use

You build and run the application using [KraftKit](https://github.com/unikraft/kraftkit).
Follow the specific instructions in the `README.md` file in the application directory for specifics on building and running with KraftKit and on using the application.

## Scripted Build, Run and Use

For testing, debugging and, generally, for finer-grained control over the build and run process, we generate scripts that wrap KraftKit, Make, QEMU, Firecracker and other commands.

The `config.yaml` file basic configuration for building and running the application.
It is used to generate the scripts and configuration files required to build and run the application.
To generate these files, run one of the generator scripts, depending on the application type:

* If the application is running in binary-compatibility (*bincompat*) mode, then run:

  ```console
  ../../../utils/bincompat/generate.einitrd.py
  ```

* If the application is running in native mode, then run:

  ```console
  ../../../utils/native/generate.py
  ```

The generator script uses the `config.yaml` file to generates the `scripts/` directory and the `Makefile` file used to to configure, build and run the application with Unikraft.

The `scripts/` directory has a structure similar to the one below.
Note that the output may differ on your system, depending on the compilers and compiler versions you have installed:

```text
scripts/
|-- build/
|   |-- kraft-fc-arm64.sh*
|   |-- kraft-fc-x86_64.sh*
|   |-- kraft-qemu-arm64.sh*
|   |-- kraft-qemu-x86_64.sh*
|   |-- make-fc-arm64.sh*
|   |-- make-fc-x86_64.sh*
|   |-- make-qemu-arm64.sh*
|   `-- make-qemu-x86_64.sh*
|-- defconfig/
|   |-- fc-arm64
|   |-- fc-x86_64
|   |-- qemu-arm64
|   `-- qemu-x86_64
|-- run/
|   |-- fc-arm64-initrd.json
|   |-- fc-arm64-initrd.sh*
|   |-- fc-x86_64-initrd.json
|   |-- fc-x86_64-initrd.sh*
|   |-- kraft-fc-arm64-nofs.sh*
|   |-- kraft-fc-x86_64-nofs.sh*
|   |-- kraft-qemu-arm64-nofs.sh*
|   |-- kraft-qemu-x86_64-nofs.sh*
|   |-- qemu-arm64-9pfs.sh*
|   |-- qemu-arm64-initrd.sh*
|   |-- qemu-x86_64-9pfs.sh*
|   `-- qemu-x86_64-initrd.sh*
|-- setup.sh*
`-- test/
    |-- common.sh
    |-- config
    `-- test.sh*
```

The contents of the `scripts/` directory are:

- `setup.sh`: script to clone and set up required repositories in the `workdir/` directory;
  `workdir/` will be symlinked to `.unikraft/` for KraftKit-based builds
- `defconfig/`: generated configuration files required by the Make-based build;
  they are generated from `Kraftfile`
- `build/`: generated build scripts;
  there are different build scripts for using Kraft or Make or for different platforms, architectures and compilers;
- `run/`: generated run scripts;
  there is a corresponding run script for each build output from the build phase;
  Firecracker builds also generate a corresponding `.json` file;
- `test/`: generated test scripts

To use the scripts, follow the steps below:

1. Run the `setup.sh` script to clone the required support repositories in the `workdir/` directory:

   ```console
   ./scripts/setup.sh
   ```

   The `workdir/` directory will have contents similar to:

   ```text
   workdir/
   |-- libs/
   |   |-- lwip/
   |   |-- musl/
   |   `-- nginx/
   `-- unikraft/
   ```

1. Run a build script from the `build/` directory, such as:

   ```console
   ./scripts/build/make-qemu-x86_64.sh
   ```

   The resulting kernel image is located in the `workdir/build/` directory and is copied in the application root directory:

   ```console
   $ ls -lh nginx_qemu-x86_64
   -rwxr-xr-x 2 razvan razvan 1,8M mai  1 23:41 nginx_qemu-x86_64

   $ ls -lh workdir/build/nginx_qemu-x86_64
   -rwxr-xr-x 2 razvan razvan 1,8M mai  1 23:41 workdir/build/nginx_qemu-x86_64
   ```

1. Use the corresponding run script in the `run/` directory, such as:

   ```console
   ./scripts/run/qemu-x86_64-initrd.sh
   ```

   A successful run shows an output such as:

   ```text
   en1: Interface is up
   Powered by
   o.   .o       _ _               __ _
   Oo   Oo  ___ (_) | __ __  __ _ ' _) :_
   oO   oO ' _ `| | |/ /  _)' _` | |_|  _)
   oOo oOO| | | | |   (| | | (_) |  _) :_
    OoOoO ._, ._:_:_,\_._,  .__,_:_, \___)
             Telesto 0.16.3~3facdb22-custom
   ```

Depending on the running environment, use the following commands to close the virtual machine (if it's a server or something that keeps running):

- For KraftKit, use `Ctrl+c` to close the console output and then close the virtual machine with:

  ```console
  kraft rm --all
  ```

- For QEMU, use `Ctrl+a x` to close the virtual machine.

- For Firecracker, open a new console and use, as `root` (prefix with `sudo` if required):

  ```console
  pkill -f firecracker
  ```

## Scripted Testing

You can test the current kernel and libraries work for the application by running the testing scripts.
These scripts consist of:

* The `single_test.sh` script in the application root directory. This is used to run a full test for the application.
* The scripts in the `scripts/test/` directory.
  There are three files:
  * `common.sh` contains the basic test functions - it is sourced by `single_test.sh`
  * `test.sh` is the actual test script
  * `config` is a generated configuration file to run the tests

The steps to run the scripted tests are:

1. View and edit the `scripts/test/config` file to remove tests that are not usable or relevant.
   Typically, this means removing the `...-fc-arm64.sh` entries in the `RUN_SCRIPTS` array for tests done on x86_64 machines.
   Because Firecracker (`fc`) requires full virtualization support, this cannot be achieved on an x86_64 machine when targeting `arm64`.

   Something else may be skipping build scripts and only using run scripts by using `SKIP_BUILD=1`.

1. Run the `test.sh` script:

   ```console
   ./scripts/test/test.sh
   ```

   You will get results such as:

   ```console
   [build] kraft-fc-arm64                                     ... PASSED
   [build] kraft-qemu-arm64                                   ... PASSED
   [run]   kraft-qemu-arm64-nofs                              ... PASSED
   [build] make-qemu-arm64                                    ... PASSED
   [run]   qemu-arm64-9pfs                                    ... PASSED
   [run]   qemu-arm64-initrd                                  ... PASSED
   [build] kraft-fc-x86_64                                    ... PASSED
   [run]   kraft-fc-x86_64-nofs                               ... FAILED
   [build] make-fc-x86_64                                     ... PASSED
   [run]   fc-x86_64-initrd                                   ... PASSED
   [build] make-qemu-x86_64                                   ... PASSED
   [run]   qemu-x86_64-9pfs                                   ... PASSED
   [run]   qemu-x86_64-initrd                                 ... PASSED
   [build] kraft-qemu-x86_64                                  ... PASSED
   [run]   kraft-qemu-x86_64-nofs                             ... PASSED
   [build] make-fc-arm64                                      ... PASSED
   ```

1. Check detailed information in the testing output directory in `scripts/test/`:

   ```console
   $ ls scripts/test/2024-05-01-18:42:38/
   build-kraft-fc-arm64.log    build-kraft-qemu-x86_64.log  build-make-qemu-arm64.log   run-kraft-fc-x86_64-nofs.log    run-qemu-arm64-9pfs.log    run-qemu-x86_64-initrd.log
   build-kraft-fc-x86_64.log   build-make-fc-arm64.log      build-make-qemu-x86_64.log  run-kraft-qemu-arm64-nofs.log   run-qemu-arm64-initrd.log
   build-kraft-qemu-arm64.log  build-make-fc-x86_64.log     run-fc-x86_64-initrd.log    run-kraft-qemu-x86_64-nofs.log  run-qemu-x86_64-9pfs.log
   ```

   There is a `.log` file for each test.

1. To investigate failing tests, apart from checking the log output, you can run a single test by using the `single_test.sh` script:

   ```console
    ./single_test.sh ./scripts/run/qemu-x86_64-9pfs.sh -
   ```

### Notes

For KraftKit-based runs, the `build` step must happen before the corresponding `run` step.
This is because KraftKit `run` command relies on the directory contents filled by the `build` command.

You can view and edit different scripts for your own needs.
