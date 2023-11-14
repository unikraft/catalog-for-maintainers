# Caddy 2.7

This directory contains the definition for the `unikraft.org/caddy:2.7` image.

To run this image, [install Unikraft's companion command-line toolchain `kraft`](https://unikraft.org/docs/cli) and then you can run:

```
kraft run unikraft.org/caddy:2.7 -p 2015:2015
```

Once executed, it will open port `2015` and wait for connections, and can be queried.

## See also

- [How to run unikernels locally in Unikraft's Documentation](https://unikraft.org/docs/cli/running).
