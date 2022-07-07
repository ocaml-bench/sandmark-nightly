import os
from functools import reduce
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(HERE, "..", "..")


def format_bench_run(run):
    prefix, _ = run.variant.rsplit("_", 1)
    variant = prefix.rstrip(f"+{run.type}")
    hash_ = run.commit[:7]
    date, time = run.timestamp.split("_", 1)
    return f"{variant}+{hash_}+{time}"


def format_variant(path, bench_type):
    value = path.split("/" + bench_type + "/")[1]
    date = value.split("/")[1].split("_")[0]
    commit_id = value.split("/")[2][:7]
    variant = value.split("/")[3].split("_", 1)[0]
    return variant + "_" + date + "_" + commit_id


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
        )
        selections.append(selection)
    return selections
