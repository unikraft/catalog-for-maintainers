# Nginx 1.25

This directory contains the definition for the `unikraft.org/nginx:1.25` image running Nginx.

To run this image, [install Unikraft's companion command-line toolchain `kraft`](https://unikraft.org/docs/cli) and then you can run:

```console
kraft run -p 8080:80 unikraft.org/nginx:1.25
```

Query the server using:

```console
curl localhost:8080
```

You will get a simple index web page from Nginx.

## See also

- [How to run unikernels locally in Unikraft's Documentation](https://unikraft.org/docs/cli/running).

## Scripted Building, Running and Testing

For scripted building, running and testing, follow the instructions in the [top-level `README.md` file](../../../README.md).

The scripts use bridged networking.
So, after using a run script and starting Nginx in Unikraft, query it using:

```console
curl 172.44.0.2
```
