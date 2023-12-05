FROM --platform=linux/x86_64 rust:1.73.0-bookworm AS build

WORKDIR /src

RUN set -xe; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      wget \
      xz-utils \
      musl-dev \
      musl-tools \
      patch \
      git; \
    git clone https://github.com/fbergen/findtime \
    ;

WORKDIR /src/findtime

RUN set -xe; \
    rustup target add x86_64-unknown-linux-musl; \
    cargo build --release --target=x86_64-unknown-linux-musl \
    ;

RUN --mount=type=tmpfs,target=/etc set -xe; \
    echo "nameserver 8.8.8.8" > /etc/resolv.conf

FROM scratch

COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=build /src/findtime/target/x86_64-unknown-linux-musl/release/findtime /usr/bin/findtime
COPY --from=build /src/findtime/index.html /src/findtime/main.js /
COPY --from=build /etc/resolv.conf /etc/resolv.conf
