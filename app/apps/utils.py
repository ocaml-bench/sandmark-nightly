import json
import os

import numpy as np
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


def update_session_state_value(key, options, index=0):
    value = st.session_state.get(key, [options[index]])
    if isinstance(value, list):
        value = value[0]
    if value not in options:
        value = options[0]
    st.session_state[key] = value
    set_params_from_session()


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
        prefix = f"{type_}_{prefix}"
        col = 0
        options = sorted(
            structure.keys(),
            reverse=True,
            # Sort latest version with fewest "+" in the variant name at top
            key=lambda x: (x.split("+")[0], x.count("+") * -1, x),
        )
        index = row % len(options)
        key = f"{prefix}{col}"
        update_session_state_value(key, options, index)
        first_val = containers[row][col].selectbox(
            labels[col],
            options,
            index=index,
            key=key,
            on_change=set_params_from_session,
        )

        col = 1
        key = f"{prefix}{col}"
        dates = sorted(structure[first_val].keys(), reverse=True)
        update_session_state_value(key, dates)
        date_val = containers[row][col].selectbox(
            labels[col],
            dates,
            key=key,
            disabled=len(dates) <= 1,
            on_change=set_params_from_session,
        )

        col = 2
        key = f"{prefix}{col}"
        runs = [run for run in structure[first_val][date_val]]
        state_run = st.session_state.get(key, [runs[0].variant])
        if isinstance(state_run, list):
            for run in runs:
                if fmt_baseline(run) == state_run[0]:
                    st.session_state[key] = run
                    break
            else:
                st.session_state[key] = runs[0]
                set_params_from_session()

        selection = containers[row][col].selectbox(
            labels[col],
            runs,
            key=key,
            format_func=format_func,
            disabled=len(runs) <= 1,
            on_change=set_params_from_session,
        )
        selections.append(selection)
    return selections


def get_display_name(row, metric, baseline, df):
    name = row["name"]
    baseline_row = df[(df["name"] == name) & (df["variant"] == baseline)].dropna()
    value = np.nan if baseline_row.empty else baseline_row[metric].iloc[0]
    return f"{name} ({value:.2f})" if isinstance(value, np.floating) else f"{name} ({value})"


def add_display_name(df, baseline, metric):
    df["display_name"] = df.apply(get_display_name, axis=1, metric=metric, baseline=baseline, df=df)
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


def write_params_to_session(params):
    for key, values in params.items():
        st.session_state[key] = values


def set_params_from_session():
    SESSION_KEYS = {
        "Sequential Benchmarks": ["app", "sequential_*"],
        "Parallel Benchmarks": ["app", "parallel_*"],
        "Perfstat Output": ["app", "perfstat_*"],
        "Instrumented Pausetimes Sequential": ["app", "pausetimes_seq_*"],
        "Instrumented Pausetimes Parallel": ["app", "pausetimes_par_*"],
    }
    app_name = st.session_state.get("app", {}).get("title")
    keys = SESSION_KEYS.get(app_name, ["app"])
    wildcards = tuple(key.strip("*") for key in keys if key.endswith("*"))
    wildcard_keys = [key for key in st.session_state if key.startswith(wildcards)]
    params = {}
    for key in keys + wildcard_keys:
        if key == "app":
            value = app_name
        else:
            value = st.session_state.get(key)
            if not value:
                continue
            if value.__class__.__name__ == "BenchRun":
                value = fmt_baseline(value)
        params[key] = [value]

    st.experimental_set_query_params(**params)


def get_dataframe(file):
    """Read a bench JSON file as a Pandas dataframe."""

    with open(file) as f:
        data = []
        for l in f:
            temp = json.loads(l)
            # check if the benchmark json contains name field
            # avoids crashing if the entry doesn't contain a benchmark
            if "name" in temp:
                data.append(temp)
        df = pd.json_normalize(data)
        df["variant"] = format_variant(file)

    return df
