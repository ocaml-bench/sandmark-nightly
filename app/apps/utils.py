from functools import reduce
import streamlit as st

# [[a11, a12 ... a1n], [a21, a22 ... a2n], ... [am1, am2 ... amn]] => [a11]
def flatten(lst):
    return reduce(lambda a, b: a + b, lst)


# [(a1, b1), (a2, b2) ... (an, bn)] => ([a1, a2, ... an], [b1, b2, ... bn])
def unzip(lst):
    return list(zip(*lst))


def unzip_dict(d):
    a = unzip(list(d))
    # st.write(a)
    commit_variant_tuple_lst = [(x1, x2) for x1, x2 in zip(a[0], a[1])]
    return commit_variant_tuple_lst


def fmt_variant(commit, variant_lst):
    return [f"+{commit}_".join(v.rsplit("_", 1)) for v in variant_lst]


def unfmt_variant(variant):
    prefix, stem = variant.rsplit("_", 1)
    name, commit = prefix.rsplit("+", 1)
    return (commit, f"{name}_{stem}")


def get_selected_values(n, benches):
    containers = [st.columns(3) for i in range(n)]
    selections = []
    for i in range(n):
        # create the selectbox in columns
        host_val = containers[i][0].selectbox(
            "hostname",
            benches.structure.keys(),
            key=f"{i}0_{benches.config['bench_type']}",
        )
        timestamp_val = containers[i][1].selectbox(
            "timestamp",
            benches.structure[host_val].keys(),
            key=f"{i}1_{benches.config['bench_type']}",
        )
        commit_variant_tuple_lst = unzip_dict(
            (benches.structure[host_val][timestamp_val]).items()
        )
        fmtted_variants = [fmt_variant(c, v) for c, v in commit_variant_tuple_lst]
        fmtted_variants = flatten(fmtted_variants)
        variant_val = containers[i][2].selectbox(
            "variant", fmtted_variants, key=f"{i}2_{benches.config['bench_type']}"
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
