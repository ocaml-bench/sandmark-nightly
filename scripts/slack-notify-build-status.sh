#!/bin/bash

set -euxo pipefail

source "$(dirname "${0}")/_helpers.sh"

function commit_url {
    echo "https://github.com/ocaml-bench/sandmark-nightly/commit/${1}"
}

CHANGED_DIRS=$1
TESTING_COMMIT=$2
MAIN_COMMIT=$3
HOSTNAME=$4

TMP_WORKTREE=$(mktemp -d --suffix=.sandmark.nightly)
git --work-tree "${TMP_WORKTREE}" checkout "${TESTING_COMMIT}" -- .
git reset

for dir in ${CHANGED_DIRS}; do
    BENCH_FILE=$(find "${TMP_WORKTREE}/${dir}" -name "*.summary.bench" -type f | head -n 1)
    LOG_FILE=$(find "${TMP_WORKTREE}/${dir}" -name "*.log" -type f | head -n 1)
    if [ -n "${BENCH_FILE}" ] && \
           bench_file_has_content "${BENCH_FILE}" && \
           log_has_no_errors "${LOG_FILE}";
    then
        PASSED_BUILDS="${PASSED_BUILDS:-}\n- $(basename "${BENCH_FILE}")"
    else
        FAILED_BUILDS="${FAILED_BUILDS:-}\n- $(basename "${LOG_FILE}")"
    fi
done

if [ -n "${PASSED_BUILDS:-}" ]; then
    PASSED_BLOCK="{
                        \"type\": \"header\",
                        \"text\": {
                                \"type\": \"plain_text\",
                                \"text\": \":heavy_check_mark: Successful builds on ${HOSTNAME}\"
                        }
                },
                {
                        \"type\": \"section\",
                        \"text\": {
                                \"type\": \"mrkdwn\",
                                \"text\": \"${PASSED_BUILDS}\"
                        }
                },
                {
                        \"type\": \"section\",
                        \"text\": {
                                \"type\": \"mrkdwn\",
                                \"text\": \"Click here to see the <$(commit_url ${MAIN_COMMIT})|successful builds commit> on main\"
                        }
                },"
fi

if [ -n "${FAILED_BUILDS:-}" ]; then
    FAILED_BLOCK="{
                        \"type\": \"header\",
                        \"text\": {
                                \"type\": \"plain_text\",
                                \"text\": \":x: Failed builds on ${HOSTNAME}\"
                        }
                },
                {
                        \"type\": \"section\",
                        \"text\": {
                                \"type\": \"mrkdwn\",
                                \"text\": \"${FAILED_BUILDS}\"
                        }
                },
                {
                        \"type\": \"section\",
                        \"text\": {
                                \"type\": \"mrkdwn\",
                                \"text\": \"<!here> Click here to see the <$(commit_url ${TESTING_COMMIT})|commit> on testing\"
                        }
                }"
fi

rm -r "${TMP_WORKTREE}"


if [[ -n ${PASSED_BLOCK:-} || -n ${FAILED_BLOCK:-} ]]; then
    SLACK_TEXT="{
            \"blocks\": [
                        ${PASSED_BLOCK:-}
                        ${FAILED_BLOCK:-}
            ]
    }"
    set +x  # Don't print SLACK_API_URL in the logs...
    curl "${SLACK_API_URL}" --data-raw "${SLACK_TEXT}" -H "Content-type: application/json"
    set -x
fi
