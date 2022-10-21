#!/usr/bin/env python


def bench_file_has_content(path, n=1):
    """Ensure the bench file in a directory has at least n lines of content."""
    bench_files = list(path.glob("**/*.bench"))
    if not bench_files:
        return False, None
    bench_file = bench_files[0]
    with open(bench_file) as f:
        lines = f.readlines()
    return len(lines) > n, bench_file


def log_has_no_errors(path):
    log_files = list(path.glob("**/*.log"))
    if not log_files:
        print("Could not find log file")
        return False, None
    log_file = log_files[0]
    with open(log_file) as f:
        log_text = f.read()
    return "Error:" not in log_text, log_file


def is_valid(path):
    bench_status, bench_file = bench_file_has_content(path)
    log_status, log_file = log_has_no_errors(path)
    status = bench_status and log_status
    return dict(status=status, log_file=log_file, bench_file=bench_file)


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import sys

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

    sys.exit(not data["status"])
