FROM --platform=linux/x86_64 debian:bookworm AS build

RUN set -xe; \
    apt -yqq update; \
    apt -yqq install \
        wget \
        ca-certificates \
        build-essential \
        unzip \
    ;

ARG DUCKDB_VERSION=0.9.1

WORKDIR /src

RUN set -xe; \
    wget https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/libduckdb-linux-amd64.zip; \
    unzip -q libduckdb-linux-amd64.zip; \
    mv libduckdb.so /usr/local/lib/; \
    ldconfig /usr/local/lib/libduckdb.so \
    ;

COPY ./main.c /src/main.c

RUN set -xe; \
    gcc -Wall -I. -o /main /src/main.c -lduckdb

FROM scratch

COPY --from=build /main /main
COPY --from=build /usr/local/lib/libduckdb.so /usr/local/lib/libduckdb.so
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libgcc_s.so.1 /lib/x86_64-linux-gnu/libgcc_s.so.1
COPY --from=build /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0
COPY --from=build /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /lib/x86_64-linux-gnu/libstdc++.so.6 /lib/x86_64-linux-gnu/libstdc++.so.6
COPY --from=build /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
COPY --from=build /etc/ld.so.cache /etc/ld.so.cache
