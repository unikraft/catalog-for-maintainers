FROM --platform=linux/x86_64 python:3.12 AS build

RUN set -xe; \
    /usr/sbin/ldconfig /usr/local/lib

FROM scratch

COPY --from=build /usr/local/lib /usr/local/lib
COPY --from=build /usr/local/bin/python3 /usr/local/bin/python3
COPY --from=build /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --from=build /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/libm.so.6
COPY --from=build /usr/lib/x86_64-linux-gnu/libz.so.1 /usr/lib/x86_64-linux-gnu/libz.so.1
COPY --from=build /lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
COPY --from=build /etc/ld.so.cache /etc/ld.so.cache

COPY ./helloworld.py /helloworld.py
