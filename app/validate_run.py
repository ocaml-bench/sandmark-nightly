#!/usr/bin/env python
import json
import re
import subprocess


def bench_file_has_content(path, n=1):
    """Ensure the bench file in a directory has at least n lines of content."""
    bench_files = list(path.glob("**/*.bench"))
    if not bench_files:
        return False, None
    bench_file = bench_files[0]
    with open(bench_file) as f:
        lines = f.readlines()
    return len(lines) > n, bench_file


def get_benchmark_count(bench_file):
    if "perfstat" in bench_file.parts:
        with open(bench_file) as f:
            text = f.read().strip()
        count = text.count("Performance counter stats for '")
    else:
        text = subprocess.check_output(["jq", "-s", ".", str(bench_file)])
        count = len(json.loads(text)) - 1
    return count


def total_benchmark_count(config_json):
    with open(config_json) as f:
        data = json.load(f)
    total = sum(
        len(benchmark.get("runs", [])) for benchmark in data.get("benchmarks", [])
    )
    return total


def benchmark_fraction(path):
    has_content, bench_file = bench_file_has_content(path)
    config_jsons = [] if not bench_file else list(bench_file.parent.glob("*.json"))
    total = 0 if not config_jsons else total_benchmark_count(config_jsons[0])
    success = 0 if not has_content else get_benchmark_count(bench_file)
    return success, total, bench_file


def log_has_no_errors(path):
    log_files = list(path.glob("**/*.log"))
    if not log_files:
        print("Could not find log file")
        return False, None
    log_file = log_files[0]
    with open(log_file) as f:
        log_text = f.read()
    return not re.search(r"\bError\b", log_text), log_file


def is_valid(path):
    log_status, log_file = log_has_no_errors(path)
    success, total, bench_file = benchmark_fraction(path)
    # For older benchmark runs, we don't have the data for total benchmarks. In
    # that case, we continue to use the old metric for success -- bench file
    # has content and log file has no errors. When we have data for total
    # number of benchmarks, we mark a run as successful if at least one
    # benchmark ran successfully.
    bench_status = success > 0
    STATUS_EMOJI = {True: "✅", False: "❌"}
    status_text = (
        f"{success} of {total}"
        if total > 0
        else STATUS_EMOJI[bench_status and log_status]
    )
    return dict(
        status=bench_status if total > 0 else bench_status and log_status,
        status_text=status_text,
        log_has_errors=log_status,
        successful_benchmarks=success,
        total_benchmarks=total,
        log_file=log_file,
        bench_file=bench_file,
    )


if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to a results directory")

    args = parser.parse_args()
    path = Path(args.path)
    data = is_valid(path)
    log_file = data["log_file"]
    if not log_file:
        print("Could not file log file")
    else:
        print(f"log: {log_file}")

    bench_file = data["bench_file"]
    if not bench_file:
        print("Could not file bench file")
    else:
        print(f"bench: {bench_file}")

    successful_benchmarks = data["successful_benchmarks"]
    total_benchmarks = data["total_benchmarks"]
    print(f"count: {successful_benchmarks} of {total_benchmarks}")

    sys.exit(not data["status"])
