from nested_dict import nested_dict
import os
from collections import OrderedDict
import pandas as pd
import glob


class BenchStruct:
    config = {}

    def __init__(self, bench_type, artifacts_dir, bench_stem):
        self.structure = nested_dict(3, list)
        self.config["bench_type"] = bench_type
        self.config["artifacts_dir"] = artifacts_dir
        self.config["bench_stem"] = bench_stem

    def add(self, host, timestamp, commit, variant):
        self.structure[host][timestamp][commit].append(variant)

    def add_files(self, files):
        for relative_path in files:
            self.add(*relative_path.split("/"))

    def to_filepath(self):
        filepaths = []
        for host, timestamps in self.structure.items():
            for timestamp, commits in timestamps.items():
                for commit, bench_files in commits.items():
                    for bench_file in bench_files:
                        t = os.path.join(
                            self.config["artifacts_dir"],
                            self.config["bench_type"],
                            host,
                            timestamp,
                            commit,
                            bench_file,
                        )
                        filepaths.append(t)
        return filepaths

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
        data = list()
        for host_timestamp_commit_tuple, variant_lst in self.structure.items_flat():
            host = host_timestamp_commit_tuple[0]
            timestamp = host_timestamp_commit_tuple[1]
            commit_id = host_timestamp_commit_tuple[2]
            if len(variant_lst) > 1:
                temp_lst = [
                    [host, timestamp, commit_id, variant] for variant in variant_lst
                ]
                for l in temp_lst:
                    data.append(l)
            else:
                temp_lst = [host, timestamp, commit_id, variant_lst[0]]
                data.append(temp_lst)

        df_data = pd.DataFrame(
            data, columns=["hostname", "timestamp", "commit_id", "variant"]
        )
        return df_data
