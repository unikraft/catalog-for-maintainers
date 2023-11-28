# Wasmtime Hello Rust

This directory contains the definition to run a helloworld Rust program with [Wasmtime](https://github.com/bytecodealliance/wasmtime) on Unikraft in binary compatibility mode.

Follow the instructions in the common `../README.md` file to set up and configure the application.

## Quick Run

Use `kraft` to run the image:

```console
kraft run -M 256M
```

Once executed, it will start Wasmtime in binary compatibility mode.
Wasmtime will run the `hello.wasm` binary generated from the `hello.rs` program.
The result will be the printing of a `Hello, World!` message.

## Scripted Run

You can also use the scripted runs, detailed in the common `../README.md`.
