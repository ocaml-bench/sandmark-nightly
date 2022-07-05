def fmt_variant(commit, variant_lst):
    return [f"+{commit}_".join(v.rsplit("_", 1)) for v in variant_lst]


def unfmt_variant(variant):
    prefix, stem = variant.rsplit("_", 1)
    name, commit = prefix.rsplit("+", 1)
    return (commit, f"{name}_{stem}")
