import re

from apps.index import get_commit_id, get_the_latest_commits

from . import ROOT_DIR


def test_commit_id():
    pattern = re.compile("^commit [0-9a-f]{40}$")
    for path in ROOT_DIR.rglob("*.log"):
        commit = get_commit_id(path)
        if commit == "commit unknown":
            continue
        assert pattern.match(commit) is not None


def test_get_latest_commits():
    machines = ["turing", "navajo"]
    commits = get_the_latest_commits(machines)
    assert machines == [m for m, _ in commits]
