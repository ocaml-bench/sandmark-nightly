import streamlit as st
from re import U, split, sub
import numpy as np
import pandas as pd
from functools import reduce

from nested_dict import nested_dict
from pprint import pprint

import os
import pandas as pd
import seaborn as sns
from apps import benchstruct
from apps.utils import get_selected_values, ARTIFACTS_DIR, get_dataframe


def app():
    st.title("Instrumented Pausetimes (sequential)")
    st.info(
        "Archived Results - The current benchmarks are and do not reflect the latest nightly run"
    )
    # Problem : right now the structure is a nested dict of
    #     `(hostname * (timestamp * (variants list)) dict ) dict`
    # and this nested structure although works but it is a bit difficult to work with
    # so we need to create a class object which is a record type and add
    # functions to

    # <host 1>
    # |--- <timestamp 1>
    #         |--- <commit 1>
    #                 |--- <variant 1>
    #                 |--- <variant 2>
    #                 ....
    #                 ....
    #                 ....
    #                 |--- <variant n>
    #         |--- <commit 2>
    #                 ....
    #                 ....
    #                 ....
    #         ....
    #         ....
    #         ....
    #         |--- <commit n>
    #                 ....
    #                 ....
    #                 ....
    # ....
    # ....
    # ....
    # ....
    # |--- <timestamp n>
    #         ....
    #         ....
    # <host 2>
    # ....
    # ....
    # ....
    # <host n>

    artifacts_dir = os.path.join(ARTIFACTS_DIR, "pausetimes")
    benches = benchstruct.BenchStruct(
        "sequential",
        artifacts_dir,
        ["_1.pausetimes_trunk.summary.bench", "_1.pausetimes_multicore.summary.bench"],
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "2", key=benches.config["bench_type"]))

    selected_benches = benchstruct.BenchStruct(
        "sequential",
        artifacts_dir,
        ["_1.pausetimes_trunk.summary.bench", "_1.pausetimes_multicore.summary.bench"],
    )
    for f in get_selected_values(n, benches):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)
    selected_benches.sort()

    # Expander for showing bench files
    with st.expander("Show metadata of selected benchmarks"):
        st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        df = pd.concat(data_frames, sort=False)
        df = df.sort_values(["name"])
        ## Drop some benchmarks
        df = df[
            (df.name != "alt-ergo.fill.why")
            & (df.name != "alt-ergo.yyll.why")  # multicore version does not exist
            & (df.name != "frama-c.slevel")  # multicore version does not exist
            & (  # multicore version does not exist
                df.name != "js_of_ocaml.frama-c_byte"
            )
            & (df.name != "cpdf.merge")  # multicore version does not exist
            & (df.name != "coq.BasicSyntax.v")
            & (df.name != "coq.AbstractInterpretation.v")  # coq benchmarks not building
        ]  # Not a macro benchmark. Will be removed from subsequent runs.
        return df

    df = get_dataframes_from_files(selected_files)
    df = df.drop_duplicates(subset=["name", "variant", "max_latency"])

    def plotLatencyAt(df, at, aspect):
        fdf = df.filter(["name", "variant", at + "_latency"])
        fdf.sort_values(by=[at + "_latency"], inplace=True)
        fdf[at + "_latency"] = fdf[at + "_latency"] / 1000.0
        g = sns.catplot(
            x="name",
            y=at + "_latency",
            hue="variant",
            data=fdf,
            kind="bar",
            aspect=aspect,
        )
        g.set_xticklabels(rotation=90)
        g.ax.set_ylabel(at + " latency (microseconds)")
        g.ax.set_xlabel("Benchmarks")
        g.ax.set_yscale("log")
        return g

    st.header("Max Latency")
    with st.expander("Expand"):
        st.write(df.filter(["name", "variant", "max_latency"]))

        max_latency_g = plotLatencyAt(df, "max", 4)
        st.pyplot(max_latency_g)

    def getLatencyAt(df, percentile, idx):
        groups = df.groupby("variant")
        ndfs = []
        for group in groups:
            (v, df) = group
            count = 0
            for i, row in df.iterrows():
                df.at[i, percentile + "_latency"] = list(df.at[i, "distr_latency"])[idx]
            ndfs.append(df)
        return pd.concat(ndfs)

    df2 = getLatencyAt(df, "99.9", -1)
    st.header("99.9th Percentile Latency")
    with st.expander("Expand"):
        st.write(df2.filter(["name", "variant", "99.9_latency"]))

        g_99_9 = plotLatencyAt(df2, "99.9", 4)
        st.pyplot(g_99_9)

    df3 = getLatencyAt(df, "99", -2)
    st.header("99th Percentile Latency")
    with st.expander("Expand"):
        st.write(df3.filter(["name", "variant", "99_latency"]))

        g_99 = plotLatencyAt(df3, "99", 4)
        st.pyplot(g_99)
