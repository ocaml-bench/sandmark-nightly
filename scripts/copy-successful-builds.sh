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

CHANGED_DIRS=$(for each in ${LAST_COMMIT_FILES}; do
                   dirname "${each}"
               done | sort -u)

# Ensure the main branch is checked out
CURRENT_BRANCH=$(git branch --show-current)
if [ "${CURRENT_BRANCH}" != "main" ]; then
    git checkout -B main "${GIT_REMOTE}/main"
fi

for dir in ${CHANGED_DIRS}; do
    if echo "${LAST_COMMIT_FILES}" | grep -qoP "${dir}/.*.summary.bench"; then
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
    git diff --name-only --cached | grep -qoP "." && \
        git commit -m "Automated commit for successful benchmarks in ${TESTING_COMMIT}"
    git push "${GIT_REMOTE}" main
fi

git checkout "${CURRENT_BRANCH}"
