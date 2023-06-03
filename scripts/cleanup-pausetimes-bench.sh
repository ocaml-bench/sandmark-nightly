#!/bin/bash
# Script to fix up the bench files for pausetimes benchmarks

# The script changes the benchmark files to
# 1. contain a single benchmark JSON in a single line of the file
# 2. change the latency distribution to be a map of percentile to latency
# 3. fix max_latency field to be not a truncated integer

# Issues 2 & 3 were fixed in runtime_events_tools, but we need to fix up the
# existing files.

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <benchdir>"
    exit 1
fi

benchdir=$1

percentile_keys='["25.0000", "50.0000", "60.0000", "70.0000", "75.0000", "80.0000", "85.0000", "90.0000", "95.0000", "96.0000", "97.0000", "98.0000", "99.0000", "99.9000", "99.9900", "99.9990", "99.9999", "100.0000"]'


fix_bench () {
    bench=$1
    echo "Fixing ${bench}"
    # Convert the JSON file to a temporary file
    tmpfile=$(mktemp)
    jq -c --argjson keys "${percentile_keys}" 'if (.distr_latency|type == "array") then del(.distr_latency,.max_latency) + {"max_latency": (.distr_latency|max), "distr_latency": ([$keys, .distr_latency] | transpose | map({(.[0]|tostring): .[1]}) | add)} else . end' $bench > $tmpfile
    # Replace the original file with the temporary file
    mv "${tmpfile}" "${bench}"
}

# Use the function to convert each JSON file using jq
for bench in $(find "${benchdir}" -name "*.bench"); do
    fix_bench "$bench" || echo "Failed to fix ${bench}"
done
