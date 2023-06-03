import re

import pandas as pd
import seaborn as sns
import streamlit as st

from apps import benchstruct
from apps.utils import (
    ARTIFACTS_DIR,
    get_dataframe,
    get_selected_values,
    set_params_from_session,
    update_session_state_value,
)


def app():
    st.title("Parallel Benchmarks")

    benches = benchstruct.BenchStruct("parallel", ARTIFACTS_DIR, "_1.orunchrt.summary.bench")
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    type_ = benches.config["bench_type"]

    key = f"{type_}_num_variants"
    value = st.session_state.get(key, [1])
    if isinstance(value, list):
        st.session_state[key] = int(value[0])
    n = st.number_input(
        "Number of variants",
        min_value=1,
        max_value=5,
        key=key,
        on_change=set_params_from_session,
    )

    selected_benches = benchstruct.BenchStruct(
        "parallel", ARTIFACTS_DIR, "_1.orunchrt.summary.bench"
    )
    options = ["variant", "hostname"]
    key = f"{type_}_find_by"
    update_session_state_value(key, options)
    by = st.radio(
        "Find Benchmark By",
        options=options,
        key=key,
        horizontal=True,
        on_change=set_params_from_session,
    )
    for f in get_selected_values(n, benches, by=by):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)
    selected_benches.sort()

    # Expander for showing bench files
    st.subheader("Selected Benchmarks")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        df = pd.concat(data_frames, sort=False)
        df = df.sort_values(["name", "time_secs"])
        return df

    df = get_dataframes_from_files(selected_files)

    def renameLabel(n, topic=""):
        n = n.replace("name = ", "")
        if topic == "":
            return re.sub("_multicore\..*", "", n)
        return (
            re.sub("_multicore\..*", "", n)
            + " ("
            + str(mdf.loc[mdf["name"] == n]["b" + topic].values[0])
            + ")"
        )

    def getFastestSequential(df, topic):
        fastest_sequential = {}
        for g in df.groupby(["name"]):
            (n, d) = g
            fastest_sequential[n] = min(list(d[topic]))
        return fastest_sequential

    def normalize(sdf, mdf, topic):
        frames = []
        fastest_sequential = getFastestSequential(sdf, topic)
        for g in mdf.groupby("name"):
            (n, d) = g
            n = n.replace("_multicore", "")
            if n in fastest_sequential:
                d["n" + topic] = 1 / d[topic].div(fastest_sequential[n], axis=0)
                d["b" + topic] = int(fastest_sequential[n])
            frames.append(d)
        return pd.concat(frames, ignore_index=True)

    # Sequential runs
    sdf = df.loc[~df["name"].str.contains("multicore", regex=False), :]
    with st.expander("Show Raw data (sequential runs)"):
        st.write(sdf)

    # Multicore runs
    mdf = df.loc[df["name"].str.contains("multicore", regex=False), :]
    mdf["name"] = mdf["name"].str.replace("-ndomains_", "", regex=False)
    mdf["num_domains"] = mdf["name"].str.split(".", expand=True)[1].str.split("_", expand=True)[0]
    mdf["num_domains"] = pd.to_numeric(mdf["num_domains"])
    mdf["name"] = mdf["name"].replace("\..*?_", ".", regex=True)

    mdf = normalize(sdf, mdf, "time_secs")
    with st.expander("Show Raw data (multicore runs)"):
        st.write(mdf)
    mdf = mdf.sort_values(["name"])
    with sns.plotting_context(
        rc={
            "font.size": 14,
            "axes.titlesize": 14,
            "axes.labelsize": 14,
            "legend.fontsize": 14,
        }
    ):
        speedup_g = sns.relplot(
            x="num_domains",
            y="ntime_secs",
            hue="variant",
            col="name",
            data=mdf,
            kind="line",
            style="variant",
            markers=True,
            col_wrap=3,
            lw=3,
            height=3,
        )
        for ax in speedup_g.axes:
            ax.set_title(renameLabel(ax.title.get_text(), "time_secs"))
            ax.set_ylabel("Speedup")

    st.header("Speedup")
    st.pyplot(speedup_g)
