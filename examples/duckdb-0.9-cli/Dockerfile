FROM --platform=linux/x86_64 debian:bookworm AS build

RUN set -xe; \
    apt -yqq update; \
    apt -yqq install \
        wget \
        ca-certificates \
        build-essential \
        git \
        cmake \
        ninja-build \
        unzip \
    ;

ARG DUCKDB_VERSION=0.9.2

WORKDIR /src

RUN set -xe; \
    wget https://github.com/duckdb/duckdb/archive/refs/tags/v${DUCKDB_VERSION}.zip; \
    unzip -q v${DUCKDB_VERSION}.zip \
    ;

WORKDIR /src/duckdb-${DUCKDB_VERSION}

RUN set -xe; \
    GEN=ninja make \
    ;

FROM scratch

# DuckDB CLI binary
COPY --from=build /src/duckdb-0.9.2/build/release/duckdb /usr/local/bin/duckdb

# System libraries
COPY --from=build /lib/x86_64-linux-gnu/libstdc++.so.6 /lib/x86_64-linux-gnu/libstdc++.so.6
COPY --from=build /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6
COPY --from=build /lib/x86_64-linux-gnu/libgcc_s.so.1 /lib/x86_64-linux-gnu/libgcc_s.so.1
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2

# Test file
COPY ./test.sql /test.sql
