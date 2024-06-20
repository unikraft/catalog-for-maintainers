FROM --platform=linux/x86_64 debian:bookworm AS build

RUN set -xe; \
    apt -yqq update; \
    apt -yqq install \
        git \
        nodejs \
        npm \
    ;

RUN mkdir /src
WORKDIR /src

RUN set -xe; \
    git clone https://github.com/prisma/prisma-examples --depth=1; \
    cd prisma-examples/javascript/rest-express; \
    npm install; \
    npx prisma migrate dev --name init \
    ;

FROM scratch

# Node binary
COPY --from=build /usr/bin/node /usr/local/bin/node

# Node files
COPY --from=build /usr/share/nodejs /usr/share/nodejs

# System libraries
COPY --from=build /lib/x86_64-linux-gnu/libnode.so.108 /lib/x86_64-linux-gnu/libnode.so.108
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libz.so.1 /lib/x86_64-linux-gnu/libz.so.1
COPY --from=build /lib/x86_64-linux-gnu/libuv.so.1 /lib/x86_64-linux-gnu/libuv.so.1
COPY --from=build /lib/x86_64-linux-gnu/libbrotlidec.so.1 /lib/x86_64-linux-gnu/libbrotlidec.so.1
COPY --from=build /lib/x86_64-linux-gnu/libbrotlienc.so.1 /lib/x86_64-linux-gnu/libbrotlienc.so.1
COPY --from=build /lib/x86_64-linux-gnu/libcares.so.2 /lib/x86_64-linux-gnu/libcares.so.2
COPY --from=build /lib/x86_64-linux-gnu/libnghttp2.so.14 /lib/x86_64-linux-gnu/libnghttp2.so.14
COPY --from=build /lib/x86_64-linux-gnu/libcrypto.so.3 /lib/x86_64-linux-gnu/libcrypto.so.3
COPY --from=build /lib/x86_64-linux-gnu/libssl.so.3 /lib/x86_64-linux-gnu/libssl.so.3
COPY --from=build /lib/x86_64-linux-gnu/libicui18n.so.72 /lib/x86_64-linux-gnu/libicui18n.so.72
COPY --from=build /lib/x86_64-linux-gnu/libicuuc.so.72 /lib/x86_64-linux-gnu/libicuuc.so.72
COPY --from=build /lib/x86_64-linux-gnu/libstdc++.so.6 /lib/x86_64-linux-gnu/libstdc++.so.6
COPY --from=build /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6
COPY --from=build /lib/x86_64-linux-gnu/libgcc_s.so.1 /lib/x86_64-linux-gnu/libgcc_s.so.1
COPY --from=build /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/libpthread.so.0
COPY --from=build /lib/x86_64-linux-gnu/libdl.so.2 /lib/x86_64-linux-gnu/libdl.so.2
COPY --from=build /lib/x86_64-linux-gnu/libbrotlicommon.so.1 /lib/x86_64-linux-gnu/libbrotlicommon.so.1
COPY --from=build /lib/x86_64-linux-gnu/libicudata.so.72 /lib/x86_64-linux-gnu/libicudata.so.72
COPY --from=build /lib/x86_64-linux-gnu/librt.so.1 /lib/x86_64-linux-gnu/librt.so.1
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
COPY --from=build /etc/ld.so.cache /etc/ld.so.cache

# Distro definition
COPY --from=build /etc/os-release /etc/os-release
COPY --from=build /usr/lib/os-release /usr/lib/os-release

# rest-express + Prisma
COPY --from=build /src/prisma-examples/javascript/rest-express /rest-express
