from functools import reduce
import os

import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
USE_TEST_ARTIFACTS = bool(os.getenv("USE_TEST_ARTIFACTS"))
ARTIFACTS_DIR = ROOT if not USE_TEST_ARTIFACTS else os.path.join(ROOT, "tests", "data")


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
            index=row,
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


def get_display_name(row, metric):
    name = row["name"]
    value = row[metric]
    return f"{name} ({value:.2f})"


def add_display_name(df, variant, metric):
    df["display_name"] = df.apply(get_display_name, axis=1, metric=metric)
    return df


def normalise(df, baseline, topic, additionalTopics=[]):
    df = add_display_name(df, baseline, topic)
    items = ["name", topic, "variant", "display_name"] + additionalTopics
    df_filtered = df.filter(items=items)
    try:
        df_pivot = df_filtered.reset_index().pivot(
            index="name", columns="variant", values=[topic]
        )
    except ValueError:
        st.warning(
            "Variants selected are the same, please select different variants to generate a normalized graph"
        )
        return pd.DataFrame()
    baseline_column = (topic, baseline)
    select_columns = [c for c in df_pivot.columns if c != baseline_column]
    try:
        normalised = df_pivot.div(df_pivot[baseline_column], axis=0)[select_columns]
    except KeyError:
        st.error(
            "Baseline data is empty, please select a different baseline to generate a normalized graph"
        )
        return pd.DataFrame()
    normalised = normalised.melt(
        col_level=1, ignore_index=False, value_name="n" + topic
    ).reset_index()
    return pd.merge(normalised, df_filtered, on=["name", "variant"])
