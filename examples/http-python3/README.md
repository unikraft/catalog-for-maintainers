# HTTP Server on Python3

This directory contains the definition to run an HTTP server with [Python3](https://www.python.org/) on Unikraft in binary compatibility mode.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 512M -p 8080:8080
```

Once executed, it will run the `server.py` script and wait for connections on port `8080`.

Query the server using:

```console
curl localhost:8080
```

It will print "Hello, World!".

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Once executed, scripts will run the `server.py` script and wait for connections on port `8080`.

Query the server using:

```console
curl 172.44.0.2:8080
```

It will print "Hello, World!".

