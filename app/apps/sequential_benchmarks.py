import streamlit as st
from re import U, split, sub
import numpy as np
import pandas as pd
from functools import reduce

from nested_dict import nested_dict
from pprint import pprint

import json
import os
import pandas as pd
import pandas.io.json as pdjson
import seaborn as sns
from apps import benchstruct
from apps.utils import (
    add_display_name,
    get_selected_values,
    format_variant,
    fmt_baseline,
    ARTIFACTS_DIR,
)


def app():
    st.title("Sequential Benchmarks")

    # Problem : right now the structure is a nested dict of
    #     `(hostname * (timestamp * (variants list)) dict ) dict`
    # and this nested structure although works but it is a bit difficult to work with
    # so we need to create a class object which is a record type and add functions to

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
        "sequential", ARTIFACTS_DIR, "_1.orun.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "2", key=benches.config["bench_type"]))

    selected_benches = benchstruct.BenchStruct(
        "sequential", ARTIFACTS_DIR, "_1.orun.summary.bench"
    )
    by = st.radio("Find Benchmark By", options=["variant", "hostname"], horizontal=True)
    for f in get_selected_values(n, benches, by=by):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)

    # Expander for showing bench files
    st.subheader("Benchmarks Selected")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    unique_num_selected_files = len(set(selected_files))

    normalization_state = True

    if unique_num_selected_files < len(selected_files):
        normalization_state = False

    def dataframe_intersection(data_frames):
        intersection_set_list = [set(df["name"]) for df in data_frames]
        list_diff = list(reduce(lambda x, y: x.intersection(y), intersection_set_list))
        new_data_frames = []
        for elem in list_diff:
            for df in data_frames:
                new_data_frames.append(df[(df.name == elem)])
        list_diff.sort()
        # st.write(list_diff)
        return new_data_frames

    def get_dataframe(file):
        # json to dataframe
        # st.write(file)
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

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        new_data_frames = dataframe_intersection(data_frames=data_frames)
        df = pd.concat(new_data_frames, sort=False)
        # st.write(df)
        df.sort_values(["name"])
        return df

    def plot(df, y_axis):
        graph = sns.catplot(
            x="name", y=y_axis, hue="variant", data=df, kind="bar", aspect=4
        )
        graph.set_xticklabels(rotation=90)
        return graph

    def normalise(df, baseline, topic, normalization_state, additionalTopics=[]):
        if not normalization_state:
            st.error(
                "Redundant variants selected, please choose unique variants to compare"
            )
            return pd.DataFrame()

        else:
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
            normalised = df_pivot.div(df_pivot[baseline_column], axis=0)[select_columns]
            normalised = normalised.melt(
                col_level=1, ignore_index=False, value_name="n" + topic
            ).reset_index()
            return pd.merge(normalised, df_filtered, on=["name", "variant"])

    def plot_normalised(baseline, df, topic):
        xlabel = "Benchmarks (baseline = " + baseline + ")"
        if not df.empty:
            df = pd.DataFrame.copy(df)
            df.sort_values(by=[topic], inplace=True)
            df[topic] = df[topic] - 1
            g = sns.catplot(
                x="display_name",
                y=topic,
                hue="variant",
                data=df,
                kind="bar",
                aspect=4,
                bottom=1,
            )
            g.set_xticklabels(rotation=90)
            g.ax.legend(loc=8)
            g._legend.remove()
            g.ax.set_xlabel(xlabel)
            return g

    df = get_dataframes_from_files(selected_files)
    # df = df.drop_duplicates(subset=['name','variant'])

    st.header("Select baseline (for normalized graphs)")
    baseline_record = get_selected_values(1, selected_benches, key_prefix="B")[0]

    # FIXME : coq fails to build on domains
    # df = df[(df.name != 'coq.BasicSyntax.v') & (df.name != 'coq.AbstractInterpretation.v')]

    baseline = fmt_baseline(baseline_record)

    # Display Components

    st.header("Time")
    with st.expander("Data"):
        st.write(df)
    with st.expander("Graph", expanded=True):
        st.pyplot(plot(df.copy(), "time_secs"))

    ndf = normalise(df.copy(), baseline, "time_secs", normalization_state)
    st.header("Normalized Time")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "ntime_secs")
        if g is not None:
            st.pyplot(g)

    st.header("Top heap words")
    with st.expander("Data"):
        st.write(df)
    with st.expander("Graph", expanded=True):
        st.pyplot(plot(df.copy(), "gc.top_heap_words"))
    ndf = normalise(df.copy(), baseline, "gc.top_heap_words", normalization_state)
    st.header("Normalized top heap words")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "ngc.top_heap_words")
        if g is not None:
            st.pyplot(g)

    st.header("Max RSS (KB)")
    with st.expander("Data"):
        st.write(df)
    with st.expander("Graph", expanded=True):
        st.pyplot(plot(df.copy(), "maxrss_kB"))
    ndf = normalise(df.copy(), baseline, "maxrss_kB", normalization_state)
    st.header("Normalized Max RSS (KB)")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "nmaxrss_kB")
        if g is not None:
            st.pyplot(g)

    st.header("Major Collections")
    with st.expander("Data"):
        st.write(df)
    with st.expander("Graph", expanded=True):
        st.pyplot(plot(df.copy(), "gc.major_collections"))
    ndf = normalise(df.copy(), baseline, "gc.major_collections", normalization_state)
    st.header("Normalized major collections")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "ngc.major_collections")
        if g is not None:
            st.pyplot(g)

    st.header("Minor Collections")
    with st.expander("Data"):
        st.write(df)
    with st.expander("Graph", expanded=True):
        st.pyplot(plot(df.copy(), "gc.minor_collections"))
    ndf = normalise(df.copy(), baseline, "gc.minor_collections", normalization_state)
    st.header("Normalized minor collections")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "ngc.minor_collections")
        if g is not None:
            st.pyplot(g)
