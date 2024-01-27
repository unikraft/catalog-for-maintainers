# Catalog for Maintainers

> [!WARNING]
> This repository is used by the Unikraft Open-Source Project maintainers.
>
> For the general-purpose Community Catalog, please visit:
> https://github.com/unikraft/catalog

These are common instructions for applications in the extended maintainers catalog.
Each application gets their own directory, used for documenting, setting up, configuring, building, running, testing and debugging the application.
Common information, configuration scripts are collected together in other directories such as `utils/`.

## Instructions for Bincompat Apps

The following are common information for examples of applications running in binary compatibility (i.e. **bincompat**) mode.
Instructions assume you are running commands in the application example subdirectory.

Applications running in binary compatibility mode use [`app-elfloader`](https://github.com/unikraft/app-elfloader) images to load and run native Linux ELFs (*Executable and Linking Format* files).
The images are generated using `library/base/`.
We call them `base` images or `base` kernels.

The images are also stored in the Unikraft registry and can be pulled from there.

### Directory Contents

A typical directory for a bincompat app contains:

* `Kraftfile`: build / run rules, including pulling the `base` image
* `Dockerfile`: filesystem, including binary and libraries
* `Makefile.docker`: used to generate the root filesystem from the `Dockerfile` rules
* `README.md`: specific application instructions, such as starting and testing an application
* `config.yaml`: configuration file to generate script files to run the application
* specific application files, such as configuration files and source code files

### Common Setup

The following are required before building and running a bincompat app.
In case you have already done them for other bincompat runs, you can skip them:

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

1. Start a [BuildKit](https://docs.docker.com/build/buildkit/) container to be used by KraftKit to build the filesystem from the Dockerfile.
   While in the top-level directory of this repository, source the `utils/start-buildkit.sh` directory:

   ```console
   source utils/start-buildkit.sh
   ```

### Basic Build, Run and Use

You build and run the application using [KraftKit](https://github.com/unikraft/kraftkit).
Follow the specific instructions in the `README.md` file in the application directory for specifics on building and running with KraftKit and on using the application.

### Scripted Build, Run and Use

For testing, debugging and, generally, for finer-grained control over the build and run process, we generate scripts that wrap KraftKit, Make, QEMU, Firecracker and other commands.

The `config.yaml` file basic configuration for building and runing the application.
It is used to generate the scripts and configuration files required to build and run the application.
To generate these files, run the generator script:

```console
../../../utils/bincompat/generate.einitrd.py
```

The generator script uses the `config.yaml` file to generates the `scripts/` directory and the `Makefile` file used to to configure, build and run the application with Unikraft.

The `scripts/` directory has a structure similar to the one below.
Note that the output may differ on your system, depending on the compilers and compiler versions you have installed:

```text
scripts/
|-- build/
|   |-- kraft-fc-x86_64.sh*
|   |-- kraft-qemu-x86_64.sh*
|   |-- make-clang-13-fc-x86_64.sh*
|   |-- make-clang-13-qemu-x86_64.sh*
|   |-- make-clang-15-fc-x86_64.sh*
|   |-- make-clang-15-qemu-x86_64.sh*
|   |-- make-gcc-10-fc-x86_64.sh*
|   |-- make-gcc-10-qemu-x86_64.sh*
|   |-- make-gcc-11-fc-x86_64.sh*
|   |-- make-gcc-11-qemu-x86_64.sh*
|   |-- make-gcc-12-fc-x86_64.sh*
|   |-- make-gcc-12-qemu-x86_64.sh*
|   |-- make-gcc-9-fc-x86_64.sh*
|   `-- make-gcc-9-qemu-x86_64.sh*
|-- defconfig/
|   |-- fc-x86_64
|   `-- qemu-x86_64
|-- kernel/
|-- run/
|   |-- clang-13-fc-x86_64-nofs.json
|   |-- clang-13-fc-x86_64-nofs.sh*
|   |-- clang-13-qemu-x86_64-nofs.sh*
|   |-- clang-15-fc-x86_64-nofs.json
|   |-- clang-15-fc-x86_64-nofs.sh*
|   |-- clang-15-qemu-x86_64-nofs.sh*
|   |-- gcc-10-fc-x86_64-nofs.json
|   |-- gcc-10-fc-x86_64-nofs.sh*
|   |-- gcc-10-qemu-x86_64-nofs.sh*
|   |-- gcc-11-fc-x86_64-nofs.json
|   |-- gcc-11-fc-x86_64-nofs.sh*
|   |-- gcc-11-qemu-x86_64-nofs.sh*
|   |-- gcc-12-fc-x86_64-nofs.json
|   |-- gcc-12-fc-x86_64-nofs.sh*
|   |-- gcc-12-qemu-x86_64-nofs.sh*
|   |-- gcc-9-fc-x86_64-nofs.json
|   |-- gcc-9-fc-x86_64-nofs.sh*
|   |-- gcc-9-qemu-x86_64-nofs.sh*
|   |-- kraft-fc-x86_64-nofs.sh*
|   `-- kraft-qemu-x86_64-nofs.sh*
`-- setup.sh*
```

The contents of the `scripts/` directory are:

- `setup.sh`: script to clone and set up required repositories in the `workdir/` directory
- `defconfig/`: generated configuration files required by the Make-based build;
  they are generated from `Kraftfile`
- `build/`: generated build scripts;
  there are different build scripts for using Kraft or Make or for different platforms, architectures and compilers;
- `run/`: generated run scripts;
  there is a corresponding run script for each build output from the build phase;
  Firecracker builds also generate a corresponding `.json` file;
- `kernels/`: directory where to store generated builds (kernels).

To use the scripts, follow the steps below:

1. Run the `setup.sh` script to clone the required support repositories in the `workdir/` directory:

   ```console
   ./scripts/setup.sh
   ```

   The `workdir/` directory will have contents similar to:

   ```text
   workdir/
   |-- apps/
   |   `-- elfloader/
   |-- libs/
   |   |-- libelf/
   |   `-- lwip/
   `-- unikraft/
   ```

1. Run a build script from the `build/` directory, such as:

   ```console
   ./scripts/build/make-clang-13-fc-x86_64.sh
   ```

   The resulting kernel image is placed in the `kernels/` directory:

   ```console
   $ ls -lh scripts/kernel/clang-13-nginx_fc-x86_64
   -rwxr-xr-x 2 razvand razvand 15M Jan 27 13:42 scripts/kernel/clang-13-nginx_fc-x86_64
   ```

1. Use the corresponding run script in the `run/` directory, such as:

   ```console
   ./scripts/run/clang-13-fc-x86_64-nofs.sh
   ```

   A successful run shows an output such as:

   ```text
   1: Set IPv4 address 172.44.0.2 mask 255.255.255.0 gw 172.44.0.1
   en1: Added
   en1: Interface is up
   Powered by Unikraft Telesto (0.16.1~a922af77)
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
