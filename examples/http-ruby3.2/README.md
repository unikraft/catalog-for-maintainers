# Simple Ruby HTTP Web Server

This directory contains a simple HTTP server written in JavaScript for [Ruby](https://www.ruby-lang.org/en/) running with Unikraft in binary compatibility mode.
The image opens up a simple HTTP server and provides a simple HTML response for each request.

Follow the instructions in the common `../README.md` file to set up and configure the application.

**Note**: This currently doesn't work, it fails with:

```text
mprotect(va:0x1000035000, 4096, PROT_READ) = OK
openat(AT_FDCWD, "/http_server.rb", O_RDONLY|O_CLOEXEC|O_NONBLOCK) = fd:5
fcntl(0x5, 0x4, ...) = Invalid argument (-22)
close(fd:5) = OK
ioctl(0x2, 0x5401, ...) = 0x0
ruby: write(fd:2, "ruby: ", 6) = 6
Invalid argument -- /http_server.rb (LoadError)write(fd:2, "\x1B[1mInvalid argument -- "..., 67) = 67
write(fd:2, "\x0A", 1) = 1
rt_sigaction(0x2, 0x408ddf950, ...) = 0x0
getpid() = pid:1
getpid() = pid:1
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
