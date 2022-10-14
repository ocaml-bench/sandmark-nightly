#!/bin/bash

set -euxo pipefail

source "$(dirname "${0}")/_helpers.sh"

GIT_REMOTE="${1:-origin}"

SUCCESSFUL_BUILDS=0

# Fetch testing branch to be able to see what changed on it, etc.
# NOTE: This may not be necessary when running on testing branch in CI, but
# making sure the name origin/testing can be referenced.
git fetch "${GIT_REMOTE}" testing
# Fetch main branch to be able to switch to it, and copy stuff to it.
git fetch "${GIT_REMOTE}" main

LAST_COMMIT_FILES=$(git diff-tree --no-commit-id --name-only -r "${GIT_REMOTE}/testing" --diff-filter=d)

if ! echo "${LAST_COMMIT_FILES}" | grep -qoP ".*\.log$"; then
    echo "The last commit on testing is not an benchmark results commit."
    exit 0
fi

HOSTNAME=$(echo "${LAST_COMMIT_FILES}" | cut -d "/" -f 2 | sort -u | head -n 1)

CHANGED_DIRS=$(for each in ${LAST_COMMIT_FILES}; do
                   dirname "${each}"
               done | sort -u)

# Ensure the main branch is checked out
CURRENT_BRANCH=$(git branch --show-current)
if [ "${CURRENT_BRANCH}" != "main" ]; then
    git checkout -B main "${GIT_REMOTE}/main"
fi

for dir in ${CHANGED_DIRS}; do
    BENCH_FILE=$(echo "${LAST_COMMIT_FILES}" | grep -oP "${dir}/.*.summary.bench" | head -n 1) || true
    LOG_FILE=$(echo "${LAST_COMMIT_FILES}" | grep -oP "${dir}/.*.log" | head -n 1) || true
    if [ -n "${BENCH_FILE}" ] && \
           bench_file_has_content "${BENCH_FILE}" && \
           log_has_no_errors "${LOG_FILE}";
    then
        git checkout "${GIT_REMOTE}/testing" "${dir}"
        SUCCESSFUL_BUILDS=1
        echo "Copied ${dir}"
    else
        echo "Failed build in ${dir}"
    fi
done

TESTING_COMMIT=$(git rev-parse "${GIT_REMOTE}/testing")

if [ ${SUCCESSFUL_BUILDS} -ge 1 ]; then
    # Try to commit only if files have been staged. No files are staged, if the
    # files are already on main branch.
    git config user.email "puneeth+sandmark@tarides.com"
    git config user.name "Sandmark Nightly Bot"
    git diff --name-only --cached | grep -qoP "." && \
        git commit -m "Auto-copy successful results from ${TESTING_COMMIT} (${HOSTNAME})"
    git push "${GIT_REMOTE}" main
    MAIN_COMMIT=$(git rev-parse HEAD)
fi

git checkout "${GIT_REMOTE}/testing"

"$(dirname "${0}")/slack-notify-build-status.sh" "${CHANGED_DIRS}" "${TESTING_COMMIT}" "${MAIN_COMMIT:-}" "${HOSTNAME}"

git checkout "${CURRENT_BRANCH}"
