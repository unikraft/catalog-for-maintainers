FROM --platform=linux/x86_64 debian:bookworm AS wasmtime

ARG WASMTIME_VERSION=14.0.4

WORKDIR /wasmtime

RUN set -xe; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      wget \
      xz-utils; \
    wget https://github.com/bytecodealliance/wasmtime/releases/download/v${WASMTIME_VERSION}/wasmtime-v${WASMTIME_VERSION}-x86_64-linux.tar.xz; \
    tar xvf wasmtime-v${WASMTIME_VERSION}-x86_64-linux.tar.xz; \
    mv wasmtime-v${WASMTIME_VERSION}-x86_64-linux/wasmtime /usr/local/bin; \
    rm -rf wasmtime-v${WASMTIME_VERSION}-x86_64-linux* \
    ;

FROM --platform=linux/x86_64 rust:1.73.0-bookworm AS build

WORKDIR /src

COPY ./hello.rs /src/hello.rs

RUN set -xe; \
    rustup target add wasm32-wasi; \
    rustc --target wasm32-wasi \
      -o /hello.wasm /src/hello.rs \
    ;

FROM scratch

COPY --from=build /hello.wasm /hello.wasm
COPY --from=wasmtime /usr/local/bin/wasmtime /usr/local/bin/wasmtime
COPY --from=wasmtime /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libdl.so.2 
COPY --from=wasmtime /lib/x86_64-linux-gnu/libgcc_s.so.1 /lib/x86_64-linux-gnu/libgcc_s.so.1 
COPY --from=wasmtime /lib/x86_64-linux-gnu/librt.so.1 /lib/x86_64-linux-gnu/librt.so.1 
COPY --from=wasmtime /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0 
COPY --from=wasmtime /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6 
COPY --from=wasmtime /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6 
COPY --from=wasmtime /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2 
