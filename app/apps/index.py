import pathlib

import streamlit as st

HERE = pathlib.Path(__file__).parent


def get_commit_id(path):
    with open(path, "rb") as file_:
        for line in file_:
            # commit keyword points to the latest commit of sandmark
            if line.startswith(b"commit"):
                return line.decode("utf8")
    return "commit unknown"


def get_the_latest_commits(machine_list):
    cwd = pathlib.Path.cwd()
    sequential_machines_path = [
        cwd.joinpath("sequential", machine) for machine in machine_list
    ]
    logpath_list = list()
    for seq_path in sequential_machines_path:
        # max value of subdirectory (which is the timestamp) is the latest one present in nightly
        subdirs = [path.name for path in sorted(seq_path.iterdir()) if path.is_dir()]
        # get the path for the log which is added latest
        log = [
            str(path) for path in sorted(seq_path.joinpath(max(subdirs)).rglob("*.log"))
        ]
        # the log file doesn't matter for the sandmark commit used so any file will do
        first_log = log[0]
        commit_dir = first_log.split(".")[-2]
        logpath_list.append(first_log)

    commit_list = [
        (logpath.split("/")[-4], get_commit_id(logpath).split()[1].strip())
        for logpath in logpath_list
    ]
    return commit_list


def app():
    st.title("Sandmark Nightly")
    tuple_list_of_info = get_the_latest_commits(["turing", "navajo"])
    with open(HERE / ".." / "pages" / "index.md") as f:
        st.markdown(f.read(), unsafe_allow_html=True)
    st.header("Sandmark info")
    st.subheader("Latest commit")
    for machine, commit in tuple_list_of_info:
        st.text(machine + " | " + commit)
