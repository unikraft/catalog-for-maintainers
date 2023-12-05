# Findtime

This directory contains the [Findtime](https://github.com/fbergen/findtime) runtime on Unikraft, in binary compatibility mode.
It implements a Findtime instance running on Unikraft.

## Run and Use

Use `kraft` to run the image and start a Unikraft instance:

```bash
kraft run --rm -M 128M -p 8080:8080 --plat qemu --arch x86_64 unikraft.org/findtime:master
```

If the `--plat` argument is left out, it defaults to `qemu`.
If the `--arch` argument is left out, it defaults to your system's CPU architecture.

Once executed, it will open port `8080` and wait for connections.
To test it, point your browser to http://localhost:8080.
You should see Findtime's interface.

## Inspect and Close

To list information about the Unikraft instance, use:

```bash
kraft ps
```

```text
TODO
```

The instance name is `keen_nonja`.
To close the Unikraft instance, close the `kraft` process (e.g., via `Ctrl+c`) or run:

```bash
kraft rm keen_nonja
```

## Build and Run Locally

The commands so far used the pre-build Findtime image available in the Unikraft registry.

In oder to to build a local Findtime image, clone this repository and `cd` into this directory.
Then use `kraft` to build an image locally:

```bash
kraft build --no-cache --no-update --plat qemu --arch x86_64
```

Similar to the `kraft run` command, if the `--plat` argument is left out, it defaults to `qemu`.
If the `--arch` argument is left out, it defaults to your system's CPU architecture.

In order to run the locally built image, use `.` (_dot_, the current directory)  as the final argument to the `kraft run` command:

```bash
kraft run --rm -M 128M -p 8080:8080 --plat qemu --arch x86_64 .
```

Same as above, it will open port `8080` and wait for connections.

## `kraft` and `sudo`

Mixing invocations of `kraft` and `sudo` can lead to unexpected behavior.
Read more about how to start `kraft` without `sudo` at [https://unikraft.org/sudoless](https://unikraft.org/sudoless).

## Learn More

- [How to run unikernels locally](https://unikraft.org/docs/cli/running)
- [How to build `Dockerfile` root filesystems with BuildKit](https://unikraft.org/guides/building-dockerfile-images-with-buildkit)
