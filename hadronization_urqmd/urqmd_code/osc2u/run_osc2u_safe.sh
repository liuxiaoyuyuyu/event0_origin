#!/bin/bash

# Safe wrapper for osc2u.e that handles EOF errors gracefully
# Usage: ./run_osc2u_safe.sh input_file

input_file="$1"
if [ -z "$input_file" ]; then
    echo "Usage: $0 input_file"
    exit 1
fi

if [ ! -f "$input_file" ]; then
    echo "Error: Input file $input_file not found"
    exit 1
fi

# Run osc2u.e and capture output to log
./osc2u.e < "$input_file" > run.log 2>&1
exit_code=$?

# Check if the error is just EOF (which is expected)
if [ $exit_code -ne 0 ]; then
    if grep -q "End of file" run.log || grep -q "Fortran runtime error: End of file" run.log; then
        # EOF is expected, continue silently
        exit_code=0
    else
        # Real error occurred
        exit $exit_code
    fi
fi

# Check if fort.14 was created successfully
if [ -f "fort.14" ]; then
    exit 0
else
    exit 1
fi

exit 0
