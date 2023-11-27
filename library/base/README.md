# Base / ELF Loader Build

Build `base` image (ELF Loader).
It's a plain `base` build, without an embedded initrd and without automount.
This means you rely on the root filesystem being passed as an initial ramdisk argument.
And use the `vfs.fstab`boot  options to mount the root filesystem.

Note that the build uses the `testing` branch for the [`unikraft` core repository](https://github.com/unikraft/unikraft/) and the `staging` branch for the libraries repositories ([`lib-libelf`](https://github.com/unikraft/lib-libelf/) and [`lib-lwip`](https://github.com/unikraft/lib-lwip/)) and the [`app-elfloader` base repository](https://github.com/unikraft/app-elfloader/).
This is to have the latest changes integrated in the `base` build.

## Build

Build the `base` image using:

```console
rm -fr .config* .unikraft/
kraft build --no-cache --plat qemu --arch x86_64
kraft build --no-cache --plat fc --arch x86_64
```

The kernel `base` images are in the `.unikraft/build/` directory:

```console
ls .unikraft/build/base_{fc,qemu}-x86_64
```

You get the output:

```text
.unikraft/build/base_fc-x86_64  .unikraft/build/base_qemu-x86_64
```

## Package

Package the `base` image using:

```console
kraft pkg --strategy overwrite --name index.unikraft.io/unikraft.org/base:latest
```

Include both build targets (`fc/x86_64` and `qemu/x86_64`) for a complete build.

The image is now part of the local registry:

```console
kraft pkg ls --all
```

You'll get, as part of the output:

```text
app   index.unikraft.io/unikraft.org/base                                          latest     oci     a0fb67e   61c31d3  qemu/x86_64
app   index.unikraft.io/unikraft.org/base                                          latest     oci     2559ecc   61c31d3  fc/x86_64
```

## Push

With access to the Unikraft registry, push the `base` image to the registry using:

```console
kraft pkg push index.unikraft.io/unikraft.org/base:latest
```

## Export Locally

You can also export kernel images locally (they are already part of `.unikraft/build/`):

```console
kraft pkg pull -w base-qemu index.unikraft.io/unikraft.org/base:latest
kraft pkg pull --plat fc -w base-fc index.unikraft.io/unikraft.org/base:latest
```

## Use

You use the `base:latest` image in conjunction with binary compatible apps part of the `examples/` directory.
Follow instructions there.
