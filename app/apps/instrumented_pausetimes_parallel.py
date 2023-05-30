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
    st.title("Instrumented Pausetimes (parallel)")

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

    benches = benchstruct.BenchStruct(
        "pausetimes_par", ARTIFACTS_DIR, "_1.pausetimes.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    type_ = benches.config["bench_type"]

    st.header("Select variants")
    key = f"{type_}_num_variants"
    value = st.session_state.get(key, [2])
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
        "pausetimes_par", ARTIFACTS_DIR, "_1.pausetimes.summary.bench"
    )

    options = ["variant", "hostname"]
    key = f"{type_}_find_by"
    update_session_state_value(key, options)
    by = st.radio(
        "Find Benchmark By",
        options=options,
        horizontal=True,
        key=key,
        on_change=set_params_from_session,
    )

    for f in get_selected_values(n, benches):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)

    st.subheader("Benchmarks Selected")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        df = pd.concat(data_frames, sort=False, ignore_index=True)

        mdf = df.loc[df["name"].str.contains(".*multicore.*", regex=True), :]
        mdf["num_domains"] = (
            mdf["name"].str.split(".", expand=True)[1].str.split("_", expand=True)[0]
        )
        mdf["num_domains"] = pd.to_numeric(mdf["num_domains"])
        mdf["name"] = mdf["name"].replace("\..*?_", ".", regex=True)

        mdf = mdf.drop_duplicates(subset=["name", "variant", "max_latency", "num_domains"])
        mdf = mdf.sort_values(["name"])
        return mdf

    mdf = get_dataframes_from_files(selected_files)

    def renameForLatency(n):
        n = n.replace("name = ", "")
        return re.sub("_multicore\..*", "", n)

    def plotLatencyAt(df, column_name, ylabel):
        fdf = df.filter(["name", "variant", column_name, "num_domains"])
        fdf.sort_values(by="name", inplace=True)
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
                y=column_name,
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
                ax.set_ylabel(ylabel + " latency (ms)")
                ax.set_xlabel("# Domains")
                ax.set_yscale("log")
            return g

    st.header("Max Latency")
    column_name = "max_latency"
    with st.expander("Data"):
        st.write(mdf.filter(["name", "variant", column_name, "num_domains"]))
    with st.expander("Graph", expanded=True):
        max_latency_g = plotLatencyAt(mdf, "max_latency", ylabel="max")
        st.pyplot(max_latency_g)

    st.header("99.9th Percentile Latency")
    column_name = "distr_latency.99.9000"
    with st.expander("Data"):
        st.write(mdf.filter(["name", "variant", column_name, "num_domains"]))
    with st.expander("Graph", expanded=True):
        g_99_9 = plotLatencyAt(mdf, column_name, ylabel="99.9th %ile")
        st.pyplot(g_99_9)

    st.header("99th Percentile Latency")
    column_name = "distr_latency.99.0000"
    with st.expander("Data"):
        st.write(mdf.filter(["name", "variant", column_name, "num_domains"]))
    with st.expander("Graph", expanded=True):
        g_99 = plotLatencyAt(mdf, column_name, ylabel="99th %ile")
        st.pyplot(g_99)

    # FIXME: Uncomment when Sandmark updates to the latest runtime_events_tools
    # st.header("Mean Latency")
    # with st.expander("Data"):
    #     st.write(mdf.filter(["name", "variant", "mean_latency", "num_domains"]))
    # with st.expander("Graph", expanded=True):
    #     mean_latency_g = plotLatencyAt(mdf, "mean_latency", ylabel="mean")
    #     st.pyplot(mean_latency_g)
