from functools import reduce

import pandas as pd
import seaborn as sns
import streamlit as st

from apps import benchstruct
from apps.utils import (
    ARTIFACTS_DIR,
    fmt_baseline,
    get_dataframe,
    get_selected_values,
    normalise,
    set_params_from_session,
    update_session_state_value,
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

    benches = benchstruct.BenchStruct("sequential", ARTIFACTS_DIR, "_1.orun.summary.bench")
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    type_ = benches.config["bench_type"]

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

    selected_benches = benchstruct.BenchStruct("sequential", ARTIFACTS_DIR, "_1.orun.summary.bench")

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
    for f in get_selected_values(n, benches, by=by):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)

    # Expander for showing bench files
    st.subheader("Benchmarks Selected")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

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

    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        new_data_frames = dataframe_intersection(data_frames=data_frames)
        df = pd.concat(new_data_frames, sort=False)
        # st.write(df)
        df.sort_values(["name"])
        return df

    def plot(df, y_axis):
        graph = sns.catplot(x="name", y=y_axis, hue="variant", data=df, kind="bar", aspect=4)
        graph.set_xticklabels(rotation=90)
        return graph

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
    st.header("Normalized Time")
    ndf = normalise(df.copy(), baseline, "time_secs")
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
    st.header("Normalized top heap words")
    ndf = normalise(df.copy(), baseline, "gc.top_heap_words")
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
    st.header("Normalized Max RSS (KB)")
    ndf = normalise(df.copy(), baseline, "maxrss_kB")
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
    st.header("Normalized major collections")
    ndf = normalise(df.copy(), baseline, "gc.major_collections")
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
    st.header("Normalized minor collections")
    ndf = normalise(df.copy(), baseline, "gc.minor_collections")
    with st.expander("Data"):
        st.write(ndf)
    with st.expander("Graph", expanded=True):
        g = plot_normalised(baseline, ndf, "ngc.minor_collections")
        if g is not None:
            st.pyplot(g)
