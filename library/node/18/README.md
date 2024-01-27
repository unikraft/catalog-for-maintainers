# NodeJS 18

This directory contains the definition for the `unikraft.org/node:18` image starting a simple HTTP server.

To run this image, [install Unikraft's companion command-line toolchain `kraft`](https://unikraft.org/docs/cli) and then you can run:

```console
kraft run -p 8080:8080 unikraft.org/node:18
```

Query the server using:

```console
curl localhost:8080
```

You will get a `Hello, World!` message.

## See also

- [How to run unikernels locally in Unikraft's Documentation](https://unikraft.org/docs/cli/running).

## Scripted Building, Running and Testing

For scripted building, running and testing, follow the instructions in the [top-level `README.md` file](../../../README.md).

The scripts use bridged networking.
So, after using a run script and starting the Node application in Unikraft, query it using:

```console
curl 172.44.0.2:8080
```
