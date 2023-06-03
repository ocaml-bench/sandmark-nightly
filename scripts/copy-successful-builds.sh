#!/bin/bash

set -euxo pipefail

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

TMP_WORKTREE=$(mktemp -d --suffix=.sandmark.nightly)
git --work-tree "${TMP_WORKTREE}" checkout "${GIT_REMOTE}/testing" -- .
git reset

for dir in ${CHANGED_DIRS}; do
    if ./app/validate_run.py "${TMP_WORKTREE}/${dir}";
    then
        git checkout "${GIT_REMOTE}/testing" "${dir}"
        SUCCESSFUL_BUILDS=1
        echo "Copied ${dir}"
    else
        echo "Failed build in ${dir}"
    fi
done

rm -r "${TMP_WORKTREE}"

TESTING_COMMIT=$(git rev-parse "${GIT_REMOTE}/testing")

if [ ${SUCCESSFUL_BUILDS} -ge 1 ]; then

    # Fix-up any pausetimes output files.

    # NOTE: This is required because we cannot yet run the latest version of
    # runtime_events_tools in Sandmark, because `ppxlib` (a dependency) doesn't
    # work on OCaml 5.1 and 5.2.  This can be removed once we are able to run
    # the latest version of runtime_events_tools in Sandmark
    "$(dirname "${0}")/slack-notify-build-status.sh" "pausetimes_seq"
    "$(dirname "${0}")/cleanup-pausetimes-bench.sh" "pausetimes_par"

    # Try to commit only if files have been staged. No files are staged, if the
    # files are already on main branch.
    git config user.email "puneeth+sandmark@tarides.com"
    git config user.name "Sandmark Nightly Bot"
    git diff --name-only --cached | grep -qoP "." && \
        git commit -m "Auto-copy successful results from ${TESTING_COMMIT} (${HOSTNAME})"
    git push "${GIT_REMOTE}" main
    MAIN_COMMIT=$(git rev-parse HEAD)
fi

"$(dirname "${0}")/slack-notify-build-status.sh" "${CHANGED_DIRS}" "${TESTING_COMMIT}" "${MAIN_COMMIT:-}" "${HOSTNAME}"

git checkout "${CURRENT_BRANCH}"
