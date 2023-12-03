# Simple Perl HTTP Web Server

This directory contains a simple HTTP server written in JavaScript for [Perl](https://www.perl.org/) running with Unikraft in binary compatibility mode.
The image opens up a simple HTTP server and provides a simple HTML response for each request.

Follow the instructions in the common `../README.md` file to set up and configure the application.

**Note**: This currently doesn't work.
The issue is:

```text
read(fd:3, <out>"", 8192) = 0
close(fd:3) = OK
socket(AF_NETLINK, SOCK_CLOEXEC|SOCK_RAW, 0) = Address family not supported by protocol (-97)
socket(AF_INET, SOCK_CLOEXEC|SOCK_STREAM, 6) = fd:3
fcntl(0x3, 0x1, ...) = 0x0
fcntl(0x3, 0x2, ...) = 0x0
fcntl(0x3, 0x2, ...) = 0x0
ioctl(0x3, 0x5401, ...) = Function not implemented (-38)
[    1.016592] CRIT: [libkvmplat] Unhandled page fault vaddr=0, error code=0x10
[    1.017321] CRIT: Unikraft crash - Pandora (0.15.0~689db89)
[    1.017876] CRIT: Thread "perl"@0x40b5e7020
[    1.018315] CRIT: RIP: 0008:0000000000000000
[    1.018773] CRIT: RSP: 0010:000000040b79f5a8 EFLAGS: 00010246 ORIG_RAX: 0000000000000010
[    1.019600] CRIT: RAX: 000000000019a640 RBX: 0000000000000000 RCX:0000000000000000
[    1.020367] CRIT: RDX: 0000000000000000 RSI: 000000040bc10020 RDI:000000040bc28020
[    1.021127] CRIT: RBP: 000000040b79f5e0 R08: 000000040b79fa00 R09:000000040b79fa00
[    1.021917] CRIT: R10: 0000000000000003 R11: 0000000000000246 R12:000000040bc10020
[    1.022694] CRIT: R13: 0000000000000016 R14: 000000040b79f5f8 R15:000000040bc28020
[    1.023488] CRIT: Stack:
[    1.023754] CRIT:  40b79f5a8  82 96 14 00 00 00 00 00  |........|
[    1.024400] CRIT:  40b79f5b0  10 00 a0 0b 04 00 00 00  |........|
[    1.025033] CRIT:  40b79f5b8  f8 ff ff ff ff ff ff ff  |........|
[    1.025635] CRIT:  40b79f5c0  20 00 c1 0b 04 00 00 00  | .......|
[    1.026282] CRIT:  40b79f5c8  00 00 00 00 00 00 00 00  |........|
[    1.026920] CRIT:  40b79f5d0  01 00 00 00 00 00 00 00  |........|
[    1.027490] CRIT:  40b79f5d8  00 00 00 00 00 00 00 00  |........|
[    1.027961] CRIT:  40b79f5e0  20 f6 79 0b 04 00 00 00  | .y.....|
[    1.028432] CRIT: Call Trace:
[    1.028661] CRIT:  [0x0000000000000000]
[    1.028956] CRIT:  [0x000000000014a35a]
[    1.029346] CRIT:  [0x000000000012c637]
[    1.029744] CRIT:  [0x000000000012e068]
[    1.030130] CRIT:  [0x0000000000101036]
[    1.030445] CRIT:  [0x0000000000000000]
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
