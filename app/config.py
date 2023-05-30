config = {
    "Home": {"module": "index", "saved_session_keys": ["app"]},
    "Sequential Benchmarks": {
        "module": "sequential_benchmarks",
        "saved_session_keys": ["app", "sequential_*"],
    },
    "Parallel Benchmarks": {
        "module": "parallel_benchmarks",
        "saved_session_keys": ["app", "parallel_*"],
    },
    "Perfstat Output": {"module": "perfstat", "saved_session_keys": ["app", "perfstat_*"]},
    "Instrumented Pausetimes Sequential": {
        "module": "instrumented_pausetimes_sequential",
        "saved_session_keys": ["app", "pausetimes_seq_*"],
    },
    "Instrumented Pausetimes Parallel": {
        "module": "instrumented_pausetimes_parallel",
        "saved_session_keys": ["app", "pausetimes_par_*"],
    },
}
