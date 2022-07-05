from nested_dict import nested_dict
import os
from collections import OrderedDict
import pandas as pd
import glob
from dataclasses import dataclass


@dataclass
class BenchRun:
    host: str
    timestamp: str
    commit: str
    variant: str

    def filepath(self, artifacts_dir, bench_type):
        return os.path.join(
            artifacts_dir,
            bench_type,
            self.host,
            self.timestamp,
            self.commit,
            self.variant,
        )

    def __repr__(self):
        return f"+{self.commit}_".join(self.variant.rsplit("_", 1))


class BenchStruct:
    config = {}

    def __init__(self, bench_type, artifacts_dir, bench_stem):
        self.structure = nested_dict(3, list)
        self.config["bench_type"] = bench_type
        self.config["artifacts_dir"] = artifacts_dir
        self.config["bench_stem"] = bench_stem

    def add(self, host, timestamp, commit, variant):
        run = BenchRun(host=host, timestamp=timestamp, commit=commit, variant=variant)
        self.structure[host][timestamp][commit].append(run)

    def add_files(self, files):
        for relative_path in files:
            self.add(*relative_path.split("/"))

    def to_filepath(self):
        return [
            run.filepath(
                self.config["artifacts_dir"],
                self.config["bench_type"],
            )
            for _, runs in self.structure.items_flat()
            for run in runs
        ]

    def get_bench_files(self):
        root_dir = f"{self.config['artifacts_dir']}/{self.config['bench_type']}"
        pattern = f"{root_dir}/**/*{self.config['bench_stem']}"
        bench_files = glob.glob(pattern, recursive=True)
        n = len(root_dir) + 1  # root_dir path + '/'
        return [path[n:] for path in bench_files]

    def __repr__(self):
        return f"{self.structure}"

    def sort(self):
        self.structure = {
            k: OrderedDict(sorted(v.items(), reverse=True))
            for k, v in self.structure.items()
        }
        self.structure = nested_dict(self.structure)

    def display(self):
        data = []
        for _, runs in self.structure.items_flat():
            rows = [[run.host, run.timestamp, run.commit, run.variant] for run in runs]
            data.extend(rows)

        df_data = pd.DataFrame(
            data, columns=["hostname", "timestamp", "commit_id", "variant"]
        )
        return df_data
