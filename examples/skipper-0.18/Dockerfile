FROM --platform=linux/x86_64 golang:1.21.4-bookworm AS build

RUN set -xe; apt-get update ; \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
      unzip \
      ;

WORKDIR /

RUN set -xe; \
    wget -O skipper.zip "https://github.com/zalando/skipper/archive/refs/tags/v0.18.51.zip"; \
    unzip -q skipper.zip;

WORKDIR /skipper-0.18.51

RUN CGO_ENABLED=1 go build -buildmode=pie -ldflags "-linkmode external -extldflags '-static-pie'" -o /usr/local/bin/skipper ./cmd/skipper

FROM scratch

COPY --from=build /usr/local/bin/skipper /usr/local/bin/skipper
COPY example.eskip /etc/skipper/example.eskip
