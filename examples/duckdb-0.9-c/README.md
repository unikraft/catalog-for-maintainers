# DuckDB C Example

This directory contains a simple C example using the [DuckDB](https://duckdb.org) library running with Unikraft in binary compatibility mode.
The C program is extracted from [DuckDB examples](https://github.com/duckdb/duckdb/blob/main/examples/embedded-c/main.c) and it creates and uses a test database.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 128M
```

Once executed, it will print out information from the created database:

```console
```

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Running the scripts will print out information ame as above.
