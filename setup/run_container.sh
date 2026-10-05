#!/bin/bash

# Run command that mounts the current directory to /tutorial in the container.
# This allows the output files created in the container to be persisted on the host machine.
# Example usage: ./run_container.sh docker

USER_ID=$(id -u)
GROUP_ID=$(id -g)

$1 run -p 8888:8888 -v $(pwd):/tutorial -w /tutorial -u $USER_ID:$GROUP_ID johnkpark/openmm:tutorial-msbs
