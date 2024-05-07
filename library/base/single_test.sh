#!/bin/bash

source scripts/test/common.sh

if test $# -ne 1; then
    echo "Usage: $0 start_command" 1>&2
    exit 1
fi

# Clean up previous instances.
clean_up

# Start instance.
start_instance | tee out &

# Wait for start.
sleep 3

# Query instance.
test_check_message_in_file out "Hello from Unikraft!"

end_with_success
