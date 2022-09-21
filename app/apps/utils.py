from functools import reduce
import os

import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(HERE, "..", "..")


def format_bench_run_by_host(run):
    prefix, _ = run.variant.rsplit("_", 1)
    variant = prefix.rstrip(f"+{run.type}")
    hash_ = run.commit[:7]
    return f"{variant}+{hash_}+{run.timestamp}"


def format_bench_run_by_variant(run):
    prefix, _ = run.variant.rsplit("_", 1)
    variant = prefix.rstrip(f"+{run.type}")
    hash_ = run.commit[:7]
    return f"{run.host}+{hash_}+{run.timestamp}"


def format_variant(path, artifacts_dir=ARTIFACTS_DIR):
    relpath = os.path.relpath(path, artifacts_dir)
    _, host, timestamp, commit_id, variant = relpath.split("/")
    date, _ = timestamp.split("_")
    variant = variant.split("_", 1)[0]
    return f"{host}_{variant}_{date}_{commit_id[:7]}"


def fmt_baseline(record):
    date = record.timestamp.split("_")[0]
    commit = record.commit[:7]
    variant = record.variant.rsplit("_", 1)[0]
    host = record.host
    return f"{host}_{variant}_{date}_{commit}"


def get_selected_values(n, benches, key_prefix="", by="host"):
    if by == "variant":
        labels = ["variant", "date", "host"]
        structure = benches.structure_by_variant
        format_func = format_bench_run_by_variant
        column_widths = [3, 1, 2]
    else:
        labels = ["hostname", "date", "variant"]
        structure = benches.structure
        format_func = format_bench_run_by_host
        column_widths = [1, 1, 4]
    type_ = benches.config["bench_type"]
    selections = []
    containers = [st.columns(column_widths) for i in range(n)]
    for row in range(n):
        # create the selectbox in columns
        prefix = key_prefix or str(row)
        col = 0
        first_val = containers[row][col].selectbox(
            labels[col],
            sorted(structure.keys(), reverse=True),
            key=f"{prefix}{col}_{type_}",
        )
        col = 1
        dates = sorted(structure[first_val].keys(), reverse=True)
        date_val = containers[row][col].selectbox(
            labels[col], dates, key=f"{prefix}{col}_{type_}", disabled=len(dates) <= 1
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


def add_display_name(df, variant, metric):
    name_metric = {
        n: t for (t, v, n) in zip(df[metric], df["variant"], df["name"]) if v == variant
    }
    disp_name = [
        name + " (" + str(round(name_metric[name], 2)) + ")" for name in df["name"]
    ]
    df["display_name"] = pd.Series(disp_name, index=df.index)
    return df
