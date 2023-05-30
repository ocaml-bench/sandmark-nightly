import pandas as pd
import seaborn as sns
import streamlit as st

from apps import benchstruct
from apps.utils import ARTIFACTS_DIR, get_dataframe, get_selected_values


def app():
    st.title("Instrumented Pausetimes (sequential)")
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
        "pausetimes_seq", ARTIFACTS_DIR, "_1.pausetimes.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "2", key=benches.config["bench_type"]))

    selected_benches = benchstruct.BenchStruct(
        "pausetimes_seq", ARTIFACTS_DIR, "_1.pausetimes.summary.bench"
    )
    for f in get_selected_values(n, benches):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)

    st.subheader("Benchmarks Selected")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        df = pd.concat(data_frames, sort=False, ignore_index=True)
        df = df.sort_values(["name"])
        ## Drop some benchmarks
        df = df[
            (df.name != "alt-ergo.fill.why")
            & (df.name != "alt-ergo.yyll.why")  # multicore version does not exist
            & (df.name != "frama-c.slevel")  # multicore version does not exist
            & (df.name != "js_of_ocaml.frama-c_byte")  # multicore version does not exist
            & (df.name != "cpdf.merge")  # multicore version does not exist
            & (df.name != "coq.BasicSyntax.v")
            & (df.name != "coq.AbstractInterpretation.v")  # coq benchmarks not building
        ]  # Not a macro benchmark. Will be removed from subsequent runs.
        return df

    df = get_dataframes_from_files(selected_files)
    df = df.drop_duplicates(subset=["name", "variant"])

    def plotLatencyAt(df, column_name, aspect, ylabel):
        fdf = df.filter(["name", "variant", column_name])
        fdf.sort_values(by=[column_name], inplace=True)
        g = sns.catplot(
            x="name",
            y=column_name,
            hue="variant",
            data=fdf,
            kind="bar",
            aspect=aspect,
        )
        g.set_xticklabels(rotation=90)
        ylabel += " latency (milliseconds)"
        g.ax.set_ylabel(ylabel)
        g.ax.set_xlabel("Benchmarks")
        g.ax.set_yscale("log")
        return g

    st.header("Max Latency")
    with st.expander("Data"):
        st.write(df.filter(["name", "variant", "max_latency"]))
    with st.expander("Graph", expanded=True):
        max_latency_g = plotLatencyAt(df, "max_latency", 4, ylabel="max")
        st.pyplot(max_latency_g)

    st.header("99.9th Percentile Latency")
    column_name = "distr_latency.99.9000"
    with st.expander("Data"):
        st.write(df.filter(["name", "variant", column_name]))
    with st.expander("Graph", expanded=True):
        g_99_9 = plotLatencyAt(df, column_name, 4, ylabel="99.9th percentile")
        st.pyplot(g_99_9)

    st.header("99th Percentile Latency")
    column_name = "distr_latency.99.0000"
    with st.expander("Data"):
        st.write(df.filter(["name", "variant", column_name]))
    with st.expander("Graph", expanded=True):
        g_99 = plotLatencyAt(df, column_name, 4, ylabel="99th percentile")
        st.pyplot(g_99)
