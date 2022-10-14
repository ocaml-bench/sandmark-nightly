#!/bin/bash

set -euxo pipefail

function bench_file_has_content {
    count=$(wc -l < "${1}")
    return $(test "${count}" -gt 1)
}

function log_has_no_errors {
    count=$(grep -E -c "Error:" "${1}")
    return $(test "${count}" -eq 0)
}
