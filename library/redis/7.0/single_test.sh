#!/bin/bash

source scripts/test/common.sh

if test $# -ne 1; then
    echo "Usage: $0 start_command" 1>&2
    exit 1
fi

# Clean up previous instances.
clean_up

# Start instance.
start_instance

# Wait for start.
sleep 10

# Query instance.
test_ping

# Connect via netcat.
test_netcat_connect 6379

# Connect via redis-cli.
test_redis_connect

# Query via redis-cli.
test_redis_cli

end_with_success
