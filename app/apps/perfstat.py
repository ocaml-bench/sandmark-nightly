import re

import pandas as pd
import seaborn as sns
import streamlit as st

from apps import benchstruct
from apps.utils import (
    add_display_name,
    get_selected_values,
    format_variant,
    fmt_baseline,
    ARTIFACTS_DIR,
    normalise,
)


def normalise_name(row):
    n = row["name"]
    if re.search("menhir", n) and re.search("sysver", n):
        row["name"] = "menhir.sysver"
    elif re.search("menhir", n) and re.search("ocaml", n):
        row["name"] = "menhir.ocamly"
    elif re.search("menhir", n) and re.search("sql-parser", n):
        row["name"] = "menhir.sql-parser"
    elif re.search("ydump", n) and re.search("sample.json", n):
        row["name"] = "yojson_ydump.sample.json"
    elif re.search("cpdf", n) and re.search("scale-to-fit", n):
        row["name"] = "cpdf.scale"
    elif re.search("cpdf", n) and re.search("squeeze", n):
        row["name"] = "cpdf.squeeze"
    elif re.search("cpdf", n) and re.search("blacktext", n):
        row["name"] = "cpdf.blacktext"
    elif re.search("minilight", n) and re.search("roomfront", n):
        row["name"] = "minilight.roomfront"
    elif re.search("frama-c", n) and re.search("slevel", n):
        row["name"] = "frama-c.slevel"
    elif re.search("alt-ergo", n) and re.search("fill", n):
        row["name"] = "alt-ergo.fill.why"
    elif re.search("alt-ergo", n) and re.search("yyll", n):
        row["name"] = "alt-ergo.yyll.why"
    elif re.search("cubicle", n) and re.search("german", n):
        row["name"] = "cubicle.german_pfs.cub"
    elif re.search("cubicle", n) and re.search("szymanski", n):
        row["name"] = "cubicle.szymanski_at.cub"
    elif re.search("main", n):
        row["name"] = "lexifi-g2pp."


def addrow(row, variant, data):
    if row:
        normalise_name(row)
        row["instructions_M"] = int(row["instructions"] / 1000000)
        del row["instructions"]
        row["variant"] = variant
        data.append(row.copy())


def extract(field, line, row):
    m = re.search("\s*(.*)\s*" + field, line)
    if m:
        row[field] = int(m.group(1).replace(",", "").replace(" ", ""))


def plot_normalised(df, variant, topic):
    if df.empty:
        return

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
    g.ax.set_xlabel("Benchmarks")
    return g


def get_dataframe(file):
    # json to dataframe
    data = []
    row = {}
    with open(file) as f:
        variant = format_variant(file)
        for l in f:
            # Benchmark
            m = re.search("Performance.*taskset --cpu-list 5 (.*)':", l)
            if m:
                addrow(row, variant, data)  # add previous row
                row["name"] = (
                    m.group(1).replace("exe", "").replace(" ", "").replace("./", "")
                )
            extract("instructions", l, row)
            extract("context-switches", l, row)
        addrow(row, variant, data)  # add last row
    df = pd.DataFrame(data)
    return df


def get_dataframes_from_files(files):
    data_frames = [get_dataframe(file) for file in files]
    df = pd.concat(data_frames, sort=False)
    return df


def app():
    st.title("Perfstat Output")

    benches = benchstruct.BenchStruct(
        "perfstat", ARTIFACTS_DIR, "_1.perfstat.summary.bench"
    )
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = st.number_input(
        "Number of variants",
        min_value=1,
        max_value=5,
        value=2,
        key=benches.config["bench_type"],
    )

    selected_benches = benchstruct.BenchStruct(
        "perfstat", ARTIFACTS_DIR, "_1.perfstat.summary.bench"
    )
    by = st.radio("Find Benchmark By", options=["variant", "hostname"], horizontal=True)
    for f in get_selected_values(n, benches, by=by):
        selected_benches.add(f.host, f.timestamp, f.commit, f.variant)

    # Expander for showing bench files
    st.subheader("Selected Benchmarks")
    st.write(selected_benches.display())

    selected_files = selected_benches.to_filepath()

    st.header("Select baseline (for normalized graphs)")
    baseline_record = get_selected_values(1, selected_benches, key_prefix="B")[0]
    baseline = fmt_baseline(baseline_record)

    df = get_dataframes_from_files(selected_files)
    # Exclude Soli.200 benchmark
    df = df.loc[df["name"] != "soli.200"]

    st.header("Instructions")
    g = sns.catplot(
        x="name", y="instructions_M", hue="variant", data=df, kind="bar", aspect=6
    )
    g.set_xticklabels(rotation=90)
    st.pyplot(g)

    st.subheader("Normalised")
    ndf = normalise(df, baseline, "instructions_M")
    ax = plot_normalised(ndf, baseline, "ninstructions_M")
    if ax is not None:
        st.pyplot(ax)
