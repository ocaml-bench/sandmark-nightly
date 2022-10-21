#!/usr/bin/env python


def bench_file_has_content(path, n=1):
    """Ensure the bench file in a directory has at least n lines of content."""
    bench_files = list(path.glob("**/*.bench"))
    if not bench_files:
        print("Could not find bench file")
        return False
    bench_file = bench_files[0]
    print(f"bench: {bench_file}")
    with open(bench_file) as f:
        lines = f.readlines()
    return len(lines) > n


def log_has_no_errors(path):
    log_files = list(path.glob("**/*.log"))
    if not log_files:
        print("Could not find log file")
        return False
    log_file = log_files[0]
    print(f"log: {log_file}")
    with open(log_file) as f:
        log_text = f.read()
    return "Error:" not in log_text


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to a results directory")

    args = parser.parse_args()
    path = Path(args.path)
    bench_status = bench_file_has_content(path)
    log_status = log_has_no_errors(path)
    if bench_status and log_status:
        sys.exit(0)
    else:
        sys.exit(1)
