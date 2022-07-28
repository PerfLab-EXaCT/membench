#!/bin/bash

TESTS_DIR="test/cuda-samples/bin/x86_64/linux/release/*"

for test in $TESTS_DIR
do
    
    echo "Running test: $test"
    GpuMemTrack $test
done