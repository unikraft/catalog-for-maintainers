# Simple HTTP C++ Boost Server on Unikraft

This directory contains a simple HTTP server written in C++ Boost running with Unikraft in binary compatibility mode.
The image opens up a simple HTTP server and provides a simple HTML response for each request.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 128M -p 8080:8080
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
