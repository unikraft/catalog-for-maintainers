# Skipper 0.18

This directory contains the definition to run [Skipper](https://github.com/zalando/skipper) on Unikraft in binary compatibility mode.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 512M -p 9090:9090
```

Once executed, it will open port `9090` and wait for connections, and can be queried.

Query the service using:

```console
curl localhost:9090/hello
```

This doesn't work, however, probably due to some Skipper specifics.

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Once you run the the scripts, query the service:

```console
curl 172.44.0.2:9090/hello
```

This will show a `Hello, World!` message, provided by the Skipper proxy.
It means Skipper was started successfully.
