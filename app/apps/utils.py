import os
from functools import reduce
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(HERE, "..", "..")


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
        runs = [
            run
            for runs in benches.structure[host_val][timestamp_val].values()
            for run in runs
        ]
        selection = containers[i][2].selectbox(
            "variant", runs, key=f"{prefix}2_{benches.config['bench_type']}"
        )
        selections.append(
            {
                "host": selection.host,
                "timestamp": selection.timestamp,
                "commit": selection.commit,
                "variant": selection.variant,
            }
        )
    return selections
