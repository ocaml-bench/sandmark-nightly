import os
from functools import reduce
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(HERE, "..", "..")


def fmt_variants(commit, variants):
    return [f"+{commit}_".join(v.rsplit("_", 1)) for v in variants]


def unfmt_variant(variant):
    prefix, stem = variant.rsplit("_", 1)
    name, commit = prefix.rsplit("+", 1)
    return (commit, f"{name}_{stem}")


def get_selected_values(n, benches, key_prefix=""):
    containers = [st.columns(3) for i in range(n)]
    selections = []
    for i in range(n):
        # create the selectbox in columns
        prefix = key_prefix or str(i)
        host_val = containers[i][0].selectbox(
            "hostname",
            benches.structure.keys(),
            key=f"{prefix}0_{benches.config['bench_type']}",
        )
        timestamp_val = containers[i][1].selectbox(
            "timestamp",
            benches.structure[host_val].keys(),
            key=f"{prefix}1_{benches.config['bench_type']}",
        )
        commit_variants = benches.structure[host_val][timestamp_val].items()
        fmtted_variants = [
            c_v for c, vs in commit_variants for c_v in fmt_variants(c, vs)
        ]
        variant_val = containers[i][2].selectbox(
            "variant", fmtted_variants, key=f"{prefix}2_{benches.config['bench_type']}"
        )
        selected_commit, selected_variant = unfmt_variant(variant_val)
        selections.append(
            {
                "host": host_val,
                "timestamp": timestamp_val,
                "commit": selected_commit,
                "variant": selected_variant,
            }
        )
    return selections
