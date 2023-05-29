import streamlit as st
from re import U, split, sub
import numpy as np
import pandas as pd
from functools import reduce

from nested_dict import nested_dict
from pprint import pprint

import re
import pandas as pd
import seaborn as sns
from apps import benchstruct
from apps.utils import get_selected_values, ARTIFACTS_DIR, get_dataframe


def app():
    st.title("Instrumented Pausetimes (parallel)")
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
        "parallel", artifacts_dir, "_1.pausetimes_multicore.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "2", key=benches.config["bench_type"]))

    selected_benches = benchstruct.BenchStruct(
        "parallel", artifacts_dir, "_1.pausetimes_multicore.summary.bench"
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

        mdf = df.loc[df["name"].str.contains(".*multicore.*", regex=True), :]
        mdf["num_domains"] = (
            mdf["name"].str.split(".", expand=True)[1].str.split("_", expand=True)[0]
        )
        mdf["num_domains"] = pd.to_numeric(mdf["num_domains"])
        mdf["name"] = mdf["name"].replace("\..*?_", ".", regex=True)

        mdf = mdf.drop_duplicates(
            subset=["name", "variant", "max_latency", "num_domains"]
        )
        mdf = mdf.sort_values(["name"])
        return mdf

    mdf = get_dataframes_from_files(selected_files)

    def renameForLatency(n):
        n = n.replace("name = ", "")
        return re.sub("_multicore\..*", "", n)

    def plotLatencyAt(df, at):
        fdf = df.filter(["name", "variant", at + "_latency", "num_domains"])
        fdf.sort_values(by="name", inplace=True)
        fdf[at + "_latency"] = fdf[at + "_latency"] / 1000.0
        with sns.plotting_context(
            rc={
                "font.size": 14,
                "axes.titlesize": 14,
                "axes.labelsize": 14,
                "legend.fontsize": 14,
            }
        ):
            g = sns.relplot(
                x="num_domains",
                y=at + "_latency",
                hue="variant",
                col="name",
                data=fdf,
                kind="line",
                style="variant",
                markers=True,
                col_wrap=4,
                height=3,
            )
            for ax in g.axes:
                ax.set_title(renameForLatency(ax.title.get_text()))
                ax.set_ylabel(at + " latency (μs)")
                ax.set_xlabel("# Domains")
                ax.set_yscale("log")
            return g

    st.header("Max Latency")
    with st.expander("Expand"):
        # st.write(mdf)

        max_latency_g = plotLatencyAt(mdf, "max")
        st.pyplot(max_latency_g)

    def getLatencyAt(df, percentile, idx):
        groups = df.groupby("variant")
        ndfs = []
        for group in groups:
            (v, df) = group
            count = 0
            for i, row in df.iterrows():
                count += 1
                df.at[i, percentile + "_latency"] = list(df.at[i, "distr_latency"])[idx]
            print(count)
            ndfs.append(df)
        return pd.concat(ndfs)

    mdf2 = getLatencyAt(mdf, "99.9", -1)
    st.header("99.9th Percentile Latency")
    with st.expander("Expand"):
        # st.write(mdf2.filter(["name","variant","99.9_latency"]))

        g_99_9 = plotLatencyAt(mdf2, "99.9")
        st.pyplot(g_99_9)

    mdf3 = getLatencyAt(mdf, "99", -2)
    st.header("99th Percentile Latency")
    with st.expander("Expand"):
        # st.write(mdf3.filter(["name","variant","99_latency"]))

        g_99 = plotLatencyAt(mdf3, "99")
        st.pyplot(g_99)

    st.header("Mean Latency")
    st.pyplot(plotLatencyAt(mdf, "mean"))
