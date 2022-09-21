from apps.index import get_commit_id, get_the_latest_commits

from . import ROOT_DIR


def test_commit_id():
    for path in ROOT_DIR.rglob("*.log"):
        assert get_commit_id(path).startswith("commit ")


def test_get_latest_commits():
    machines = ["turing", "navajo"]
    commits = get_the_latest_commits(machines)
    assert machines == [m for m, _ in commits]
