# DuckDB CLI Example

This directory contains the [DuckDB](https://duckdb.org) CLI running with Unikraft in binary compatibility mode.
The CLI is [built from source](https://duckdb.org/dev/building.html) via `Dockerfile` as a PIE binary.
This is because [the release version](https://duckdb.org/docs/installation/index?version=latest&environment=cli&installer=binary&platform=linux) is not PIE.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 128M
```

Once executed, it will run the script in `test.sql`, resulting in the printing of an SQL query result:

```console
-- Loading resources from /test.sql
-----------------
|  age  | grade |
| int32 | int32 |
+-------|-------+
|    20 |    10 |
|    21 |     9 |
+---------------+
```

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
Running the scripts will print out information ame as above.
