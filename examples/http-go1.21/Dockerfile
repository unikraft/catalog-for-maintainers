FROM --platform=linux/x86_64 golang:1.21.3-bookworm AS build

WORKDIR /src

COPY ./http_server.go /src/http_server.go

RUN set -xe; \
    go build \
      -buildmode=pie \
      -ldflags "-linkmode external -extldflags -static-pie" \
      -tags netgo \
      -o /http_server http_server.go \
    ;

FROM scratch

COPY --from=build /http_server /http_server
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
