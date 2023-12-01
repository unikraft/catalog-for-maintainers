#!/bin/sh

export KRAFTKIT_BUILDKIT_HOST=docker-container://buildkitd
docker container inspect buildkitd > /dev/null 2>&1 || docker run -d --name buildkitd --privileged moby/buildkit:latest
test $(docker container inspect -f '{{.State.Running}}' buildkitd 2> /dev/null) = "true" || docker start buildkitd
