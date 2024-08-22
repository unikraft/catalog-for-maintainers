#!/bin/bash

clean_up()
{
    {
    # Clean up any previous instances.
    sudo pkill -9 qemu-system
    sudo pkill -9 firecracker
    kraft stop --all
    kraft rm --all
    sudo kraft stop --all
    sudo kraft rm --all

    # Remove previously created network interfaces.
    sudo ip link set dev tap0 down
    sudo ip link del dev tap0
    sudo ip link set dev virbr0 down
    sudo ip link del dev virbr0
    } > /dev/null 2>&1
}

start_instance()
{
    # Start instance.
    setsid --fork "$start_command" &
    if test $? -ne 0; then
        echo "Cannot start instance" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_ping()
{
    # Connect to instance.
    ping -c 1 172.44.0.2
    if test $? -ne 0; then
        echo "Cannot ping address 172.44.0.2" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_curl_connect()
{
    port="$1"

    # Query instance.
    curl --retry 1 --connect-timeout 1 --max-time 10 172.44.0.2:"$port"
    if test $? -ne 0; then
        echo "Cannot connect to 172.44.0.2:$port" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_curl_check_message()
{
    port="$1"
    message="$2"

    # Check server message contents.
    curl --retry 1 --connect-timeout 1 --max-time 10 172.44.0.2:"$port" | grep "$message" > /dev/null 2>&1
    if test $? -ne 0; then
        echo "Wrong message from 172.44.0.2:$port" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_netcat_connect()
{
    port="$1"

    # Check connection.
    netcat -w 3 172.44.0.2 "$port" < /dev/null > /dev/null 2>&1
    if test $? -ne 0; then
        echo "Cannot connect to 172.44.0.2:$port" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_redis_connect()
{
    redis-cli -h 172.44.0.2 < /dev/null > /dev/null 2>&1
    if test $? -ne 0; then
        echo "Cannot connect Redis client" 1>&2
        echo "FAILED"
        clean_up
        exit 1
    fi
}

test_redis_cli()
{
    redis-cli -h 172.44.0.2 set a 1 > /dev/null 2>&1
    redis-cli -h 172.44.0.2 get a > /dev/null 2>&1
    if test $? -eq 1; then
        echo "FAILED"
        echo "Cannot talk to Redis server at 172.44.0.2" 1>&2
        do_kill
        exit 1
    fi
}

end_with_success()
{
    echo "PASSED"
    clean_up
    exit 0
}

start_command="$1"
