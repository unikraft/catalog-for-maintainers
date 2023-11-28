FROM --platform=linux/x86_64 rust:1.73.0-bookworm AS build

WORKDIR /src

COPY ./http_server.rs /src/http_server.rs

RUN set -xe; \
    rustc -o /http_server /src/http_server.rs

FROM scratch

COPY --from=build /http_server /http_server
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libgcc_s.so.1 /lib/x86_64-linux-gnu/libgcc_s.so.1
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
