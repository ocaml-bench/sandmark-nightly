# NOTE: DO NOT change the keys (slugs) in the config below, since they are used
# in the URL query parameters. Changing them would break support for old URLs.
# To continue supporting some of the URLs already out there in the wild, some
# of the slugs are not consistent with the titles.
config = {
    "home": {"title": "Home", "module": "index", "saved_session_keys": ["app"]},
    "sequential-benchmarks": {
        "title": "Sequential - throughput",
        "module": "sequential_benchmarks",
        "saved_session_keys": ["app", "sequential_*"],
    },
    "sequential-latency": {
        "title": "Sequential - latency",
        "module": "pausetimes_sequential",
        "saved_session_keys": ["app", "pausetimes_seq_*"],
    },
    "parallel-benchmarks": {
        "title": "Parallel - throughput",
        "module": "parallel_benchmarks",
        "saved_session_keys": ["app", "parallel_*"],
    },
    "parallel-latency": {
        "title": "Parallel - latency",
        "module": "pausetimes_parallel",
        "saved_session_keys": ["app", "pausetimes_par_*"],
    },
    "perfstat-output": {
        "title": "Perfstat Output",
        "module": "perfstat",
        "saved_session_keys": ["app", "perfstat_*"],
    },
}
