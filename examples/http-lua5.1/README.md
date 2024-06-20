# Simple Lua HTTP Web Server

This directory contains a simple HTTP server written in JavaScript for [Lua](https://www.lua.org/) running with Unikraft in binary compatibility mode.
The image opens up a simple HTTP server and provides a simple HTML response for each request.

Follow the instructions in the common `../README.md` file to set up and configure the application.

**Note**: This currently doesn't work, it fails with:

```text
git clone https://github.com/unikraft/catalog-for-maintainers
cd catalog-for-maintainers
git remote add unikraft-upb https://github.com/unikraft-upb/catalog
git fetch unikraft-upb
git checkout -b razvand/examples/http-lua unikraft-upb/razvand/examples/http-lua
cd library/base
../../utils/bincompat/base-build-all.sh
cd ../../examples/http-lua5.1
make initrd
../../utils/bincompat/generate.py
./run-qemu-x86_64.sh ../../kernels/base_qemu-x86_64-strace
```

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 256M -p 8080:8080
```

Once executed, it will open port `8080` and wait for connections, and can be queried.

Query the service using:

```console
curl localhost:8080
```

It will print a "Hello, World!" message.

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Once you run the the scripts, query the service:

```console
curl 172.44.0.2:8080
```
