#!/bin/bash

set -euxo pipefail

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
    if dir_files=$(./app/validate_run.py "${TMP_WORKTREE}/${dir}");
    then
        bench_file=$(echo "${dir_files}" | grep -oP "^bench: \K.*")
        PASSED_BUILDS="${PASSED_BUILDS:-}\n- $(basename "${bench_file}")"
    else
        log_file=$(echo "${dir_files}" | grep -oP "^log: \K.*")
        FAILED_BUILDS="${FAILED_BUILDS:-}\n- $(basename "${log_file}")"
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
