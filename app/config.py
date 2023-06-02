config = {
    "Home": {"module": "index", "saved_session_keys": ["app"]},
    "Sequential - throughput": {
        "module": "sequential_benchmarks",
        "saved_session_keys": ["app", "sequential_*"],
    },
    "Sequential - latency": {
        "module": "pausetimes_sequential",
        "saved_session_keys": ["app", "pausetimes_seq_*"],
    },
    "Parallel - throughput": {
        "module": "parallel_benchmarks",
        "saved_session_keys": ["app", "parallel_*"],
    },
    "Parallel - latency": {
        "module": "pausetimes_parallel",
        "saved_session_keys": ["app", "pausetimes_par_*"],
    },
    "Perfstat Output": {"module": "perfstat", "saved_session_keys": ["app", "perfstat_*"]},
}
