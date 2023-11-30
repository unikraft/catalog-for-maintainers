# Simple Python 3 HTTP Web Server

This directory contains the definition to run an HTTP server written in [Python 3](https://www.python.org/) on Unikraft in binary compatibility mode.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 512M -p 8080:8080
```

Once executed, it will open port `8080` and wait for connections, and can be queried.

Query the service using:

```console
curl localhost:8080
```

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Once you run the the scripts, query the service:

```console
curl 172.44.0.2:8080
```

This will show a `Hello, World!` message, provided by the Python HTTP server.
