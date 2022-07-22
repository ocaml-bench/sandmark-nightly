import os
from functools import reduce
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(HERE, "..", "..")


def format_bench_run(run):
    prefix, _ = run.variant.rsplit("_", 1)
    variant = prefix.rstrip(f"+{run.type}")
    hash_ = run.commit[:7]
    return f"{variant}+{hash_}+{run.timestamp}"


def format_variant(path, artifacts_dir=ARTIFACTS_DIR):
    relpath = os.path.relpath(path, artifacts_dir)
    _, _, timestamp, commit_id, variant = relpath.split("/")
    date, _ = timestamp.split("_")
    variant = variant.split("_", 1)[0]
    return f"{variant}_{date}_{commit_id[:7]}"


def get_selected_values(n, benches, key_prefix=""):
    containers = [st.columns([1, 1, 4]) for i in range(n)]
    selections = []
    for i in range(n):
        # create the selectbox in columns
        prefix = key_prefix or str(i)
        host_val = containers[i][0].selectbox(
            "hostname",
            benches.structure.keys(),
            key=f"{prefix}0_{benches.config['bench_type']}",
        )
        date_val = containers[i][1].selectbox(
            "date",
            benches.structure[host_val].keys(),
            key=f"{prefix}1_{benches.config['bench_type']}",
        )
        runs = [run for run in benches.structure[host_val][date_val]]
        selection = containers[i][2].selectbox(
            "variant",
            runs,
            key=f"{prefix}2_{benches.config['bench_type']}",
            format_func=format_bench_run,
            disabled=len(runs) <= 1,
        )
        selections.append(selection)
    return selections
