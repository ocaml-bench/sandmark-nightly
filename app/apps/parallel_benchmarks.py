from re import U, split, sub
import streamlit as st
import numpy as np
import pandas as pd

from nested_dict import nested_dict
from pprint import pprint

import json
import os
import re
import pandas as pd
import pandas.io.json as pdjson
import seaborn as sns
from apps import benchstruct
from apps.utils import get_selected_values, format_variant, ARTIFACTS_DIR


def app():
    st.title("Parallel Benchmarks")

    benches = benchstruct.BenchStruct(
        "parallel", ARTIFACTS_DIR, "_1.orunchrt.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "1", key=benches.config["bench_type"]))

    selected_benches = benchstruct.BenchStruct(
        "parallel", ARTIFACTS_DIR, "_1.orunchrt.summary.bench"
    )
    by = st.radio("Find Benchmark By", options=["variant", "hostname"], horizontal=True)
    for f in get_selected_values(n, benches, by=by):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)
    selected_benches.sort()

    # Expander for showing bench files
    st.subheader("Selected Benchmarks")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    def get_dataframe(file):
        # json to dataframe
        with open(file) as f:
            data = []
            for l in f:
                temp = json.loads(l)
                if "name" in temp:
                    data.append(temp)
            df = pd.json_normalize(data)
            df["variant"] = format_variant(file)
        return df

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
    throughput_sdf = pd.DataFrame.copy(sdf)
    with st.expander("Show Raw data (sequential runs)"):
        st.write(sdf)

    # Multicore runs
    mdf = df.loc[df["name"].str.contains("multicore", regex=False), :]
    mdf["num_domains"] = (
        mdf["name"].str.split(".", expand=True)[1].str.split("_", expand=True)[0]
    )
    mdf["num_domains"] = pd.to_numeric(mdf["num_domains"])
    mdf["name"] = mdf["name"].replace("\..*?_", ".", regex=True)

    mdf = normalize(sdf, mdf, "time_secs")
    throughput_mdf = pd.DataFrame.copy(mdf)
    with st.expander("Show Raw data (multicore runs)"):
        st.write(mdf)
    # mdf.sort_values(['name','variant','num_domains'])

    # mdf = mdf.sort_values(['name'])
    # #mdf = mdf[~mdf.index.duplicated()]
    # time_g = sns.relplot(x='num_domains', y = 'time_secs', hue='variant', col='name',
    #        data=mdf, kind='line', style='variant', markers=True, col_wrap = 4,
    #        lw=5, palette="muted")

    # st.header("Time")
    # st.pyplot(time_g)

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
