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
    structure = benches.structure
    format_func = format_bench_run
    type_ = benches.config["bench_type"]
    selections = []
    labels = ["hostname", "date", "variant"]
    containers = [st.columns([1, 1, 4]) for i in range(n)]
    for row in range(n):
        # create the selectbox in columns
        prefix = key_prefix or str(row)
        col = 0
        first_val = containers[row][col].selectbox(
            labels[col], sorted(structure.keys()), key=f"{prefix}{col}_{type_}"
        )
        col = 1
        date_val = containers[row][col].selectbox(
            labels[col], structure[first_val].keys(), key=f"{prefix}{col}_{type_}"
        )
        col = 2
        runs = [run for run in structure[first_val][date_val]]
        selection = containers[row][col].selectbox(
            labels[col],
            runs,
            key=f"{prefix}{col}_{type_}",
            format_func=format_func,
            disabled=len(runs) <= 1,
        )
        selections.append(selection)
    return selections
