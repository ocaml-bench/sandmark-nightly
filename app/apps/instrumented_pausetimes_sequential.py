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
from multipledispatch import dispatch


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

    # This idea is only for sandmark nightly

    class BenchStruct(benchstruct.BenchStruct):
        def get_bench_files(self):
            bench_files = []

            # Loads file metadata
            for root, dirs, files in os.walk(
                self.config["artifacts_dir"] + "/" + self.config["bench_type"]
            ):
                for file in files:
                    if file.endswith(self.config["bench_stem"][0]) or file.endswith(
                        self.config["bench_stem"][1]
                    ):
                        f = root.split("/" + self.config["bench_type"])
                        bench_files.append((os.path.join(root, file)))

            return bench_files

    current = os.getcwd().split("/")
    current.pop()
    artifacts_dir = "/".join(current) + "/sandmark-nightly" + "/pausetimes"
    benches = BenchStruct(
        "sequential",
        artifacts_dir,
        ["_1.pausetimes_trunk.summary.bench", "_1.pausetimes_multicore.summary.bench"],
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input("Number of variants", "2", key=benches.config["bench_type"]))

    containers = [st.columns(3) for i in range(n)]

    # [[a11, a12 ... a1n], [a21, a22 ... a2n], ... [am1, am2 ... amn]] => [a11]
    def flatten(lst):
        return reduce(lambda a, b: a + b, lst)

    # [(a1, b1), (a2, b2) ... (an, bn)] => ([a1, a2, ... an], [b1, b2, ... bn])
    def unzip(lst):
        return list(zip(*lst))

    def unzip_dict(d):
        a = unzip(list(d))
        # st.write(a)
        (x, y) = a[0], flatten(a[1])
        return (x, y)

    @dispatch(str)
    def fmt_variant(file):
        variant = file.split("/")[-1].split("_1")[0]
        commit_id = file.split("/")[-2][:7]
        date = file.split("/")[-3].split("_")[0]
        return str(variant + "_" + date + "_" + commit_id)

    @dispatch(str, str)
    def fmt_variant(commit, variant):
        # st.write(variant.split('_'))
        return (
            variant.split("_")[0]
            + "+"
            + str(commit)
            + "_"
            + variant.split("_")[1]
            + "_"
            + variant.split("_")[2]
        )

    def unfmt_variant(variant):
        commit = variant.split("_")[0].split("+")[-1]
        variant_root = variant.split("_")[1] + "_" + variant.split("_")[2]
        # st.write(variant_root)
        variant_stem = variant.split("_")[0].split("+")
        variant_stem.pop()
        variant_stem = reduce(
            lambda a, b: b if a == "" else a + "+" + b, variant_stem, ""
        )
        new_variant = variant_stem + "_" + variant_root
        # st.write(new_variant)
        return (commit, new_variant)

    def get_selected_values(n):
        lst = []
        for i in range(n):
            # create the selectbox in columns
            host_val = containers[i][0].selectbox(
                "hostname",
                benches.structure.keys(),
                key=str(i) + "0_" + benches.config["bench_type"],
            )
            timestamp_val = containers[i][1].selectbox(
                "timestamp",
                benches.structure[host_val].keys(),
                key=str(i) + "1_" + benches.config["bench_type"],
            )
            # st.write((benches.structure[host_val][timestamp_val]).items())
            if (benches.structure[host_val][timestamp_val]).items():
                commits, variants = unzip_dict(
                    (benches.structure[host_val][timestamp_val]).items()
                )
                # st.write(variants)
                fmtted_variants = [fmt_variant(c, v) for c, v in zip(commits, variants)]
                # st.write(fmtted_variants)
                variant_val = containers[i][2].selectbox(
                    "variant",
                    fmtted_variants,
                    key=str(i) + "2_" + benches.config["bench_type"],
                )
                selected_commit, selected_variant = unfmt_variant(variant_val)
                lst.append(
                    {
                        "host": host_val,
                        "timestamp": timestamp_val,
                        "commit": selected_commit,
                        "variant": selected_variant,
                    }
                )

        return lst

    selected_benches = BenchStruct(
        "sequential",
        artifacts_dir,
        ["_1.pausetimes_trunk.summary.bench", "_1.pausetimes_multicore.summary.bench"],
    )
    _ = [
        selected_benches.add(f["host"], f["timestamp"], f["commit"], f["variant"])
        for f in get_selected_values(n)
    ]
    selected_benches.sort()

    # Expander for showing bench files
    with st.expander("Show metadata of selected benchmarks"):
        st.write(selected_benches.structure)

    selected_files = selected_benches.to_filepath()

    def get_dataframe(file):
        # json to dataframe

        with open(file) as f:
            data = []
            for l in f:
                data.append(json.loads(l))
            df = pdjson.json_normalize(data)
        df["variant"] = fmt_variant(file)

        return df

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
