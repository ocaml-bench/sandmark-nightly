import datetime
import os
from pathlib import Path
import subprocess

import pandas as pd
import streamlit as st

from validate_run import is_valid

ROOT = Path(__file__).parent.parent.parent
GLOB_PAT = "**/{date:%Y%m%d}_*/**/*.log"


@st.cache(ttl=300)
def checkout_testing_branch():
    path = "/tmp/sandmark-nightly-testing-branch"
    branch = "testing"
    os.makedirs(path, exist_ok=True)
    subprocess.check_call(["git", "fetch", "--force", "origin", f"{branch}:{branch}"])
    subprocess.check_call(["git", "--work-tree", path, "checkout", branch, "--", "."])
    subprocess.check_call(["git", "reset"])
    return path


def collect_run_statuses(root, start_date):
    dates = [start_date - datetime.timedelta(days=n) for n in range(7)]
    paths = [
        (date, path.parent)
        for date in dates
        for path in root.glob(GLOB_PAT.format(date=date))
    ]
    validity = []
    for date, path in paths:
        run = is_valid(path)
        validity.append(run)
        run["date"] = date
        log_file = run["log_file"]
        if log_file:
            run["variant"] = log_file.name.rsplit(".", 3)[0]
            run["log_file"] = str(log_file)
            run["host"] = log_file.relative_to(root).parts[1]
        else:
            run["host"] = "unknown"

    validity = pd.DataFrame(
        validity, columns=["status", "date", "log_name", "host", "log_file", "variant"]
    )
    validity = validity.pivot_table(
        index=["variant", "host"],
        columns=["date"],
        values="status",
        aggfunc={"status": lambda x: x},
    )
    validity.columns = sorted(validity.columns, reverse=True)
    return validity


def main():
    title = "Sandmark Nightly Build Status"
    st.set_page_config(page_title=title, page_icon="🐫", layout="wide")
    st.title(title)

    date = datetime.date.today()
    path = checkout_testing_branch()
    st.write(collect_run_statuses(Path(path), date))


if __name__ == "__main__":
    main()
