# Nginx

This directory contains configuration for [Nginx](https://nginx.org/) running with Unikraft in binary compatibility mode.
The image opens up an Nginx server waiting for connections.

Follow the instructions in the common `../../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 512M -p 8080:80
```

Once executed, it will open port `8080` and wait for connections, and can be queried.

Query the service using:

```console
curl localhost:8080
```

It will print a simple HTML landing page.

## Scripted Run

Use the scripted runs, detailed in the common `../../README.md`.
Once you run the the scripts, query the service:

```console
curl 172.44.0.2
```
