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
sleep 3

# Query instance.
test_ping

# Connect via HTTP.
test_curl_connect 8080

# Connect via HTTP.
test_curl_check_message 8080 "Hello, World!"

end_with_success
