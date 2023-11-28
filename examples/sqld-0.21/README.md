# sqld

This directory contains the definition to run [sqld](https://github.com/tursodatabase/libsql/tree/main/libsql-server) on Unikraft in binary compatibility mode.

Follow the instructions in the common `../README.md` file to set up and configure the application.

**Note**: Currently, Unikraft sqld runs don't work due to lack of UNIX socket support.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 256M -p 8080:8080
```

This starts an SQL server waiting for HTTP connection on port `8080`.
You can use [client libraries](https://github.com/tursodatabase/libsql/blob/main/docs/BUILD-RUN.md#query-sqld) to query it.

## Scripted Run

Use the scripted runs, detailed in the common `../README.md`.
They will starts an SQL server waiting for HTTP connection on port `8080`.
