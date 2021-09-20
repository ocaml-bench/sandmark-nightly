import streamlit as st
from re import U, split, sub
import numpy as np
import pandas as pd
from functools import reduce

from nested_dict import nested_dict
from pprint import pprint

import json
import os
import pandas as pd
import pandas.io.json as pdjson
import seaborn as sns
from apps import benchstruct
from multipledispatch import dispatch

def app():
    st.title("Instrumented Pausetimes (parallel)")

	# Problem : right now the structure is a nested dict of
	#     `(hostname * (timestamp * (variants list)) dict ) dict`
	# and this nested structure although works but it is a bit difficult to work with
	# so we need to create a class object which is a record type and add
	# functions to

	# <host 1>
	# |--- <timestamp 1>
	#         |--- <commit 1>
	#                 |--- <variant 1>
	#                 |--- <variant 2>
	#                 ....
	#                 ....
	#                 ....
	#                 |--- <variant n>
	#         |--- <commit 2>
	#                 ....
	#                 ....
	#                 ....
	#         ....
	#         ....
	#         ....
	#         |--- <commit n>
	#                 ....
	#                 ....
	#                 ....
	# ....
	# ....
	# ....
	# ....
	# |--- <timestamp n>
	#         ....
	#         ....
	# <host 2>
	# ....
	# ....
	# ....
	# <host n>

	# This idea is only for sandmark nightly

    class BenchStruct(benchstruct.BenchStruct):
        
        def get_bench_files(self):
            bench_files = []

            # Loads file metadata
            for root, dirs, files in os.walk(self.config["artifacts_dir"] + "/" + self.config["bench_type"]):
                for file in files:
                    if file.endswith(self.config["bench_stem"]):
                        f = root.split("/" + self.config["bench_type"])
                        bench_files.append((os.path.join(root,file)))
            
            return bench_files

    current = os.getcwd().split('/')
    current.pop()
    artifacts_dir = '/'.join(current) + '/pausetimes'
    print(artifacts_dir)

    benches = BenchStruct("parallel", artifacts_dir, "_1.pausetimes_multicore.summary.bench")
    benches.add_files(benches.get_bench_files())
    benches.sort()

    st.header("Select variants")
    n = int(st.text_input('Number of variants','2', key=benches.config["bench_type"]))

    containers = [st.columns(3) for i in range(n)]

    # [[a11, a12 ... a1n], [a21, a22 ... a2n], ... [am1, am2 ... amn]] => [a11]
    def flatten(lst):
        return reduce(lambda a, b: a + b, lst)

    # [(a1, b1), (a2, b2) ... (an, bn)] => ([a1, a2, ... an], [b1, b2, ... bn])
    def unzip(lst):
        return (list(zip(*lst)))

    def unzip_dict(d):
        a = unzip(list(d))
        # st.write(a)
        (x, y) = a[0], flatten(a[1])
        return (x, y)
    
    @dispatch(str)
    def fmt_variant(file):
        variant   = file.split('/')[-1].split('_1')[0]
        commit_id = file.split('/')[-2][:7]
        date      = file.split('/')[-3].split('_')[0]
        return str(variant + "_" + date + "_" + commit_id)

    @dispatch(str,str)
    def fmt_variant(commit, variant):
        # st.write(variant.split('_'))
        return (variant.split('_')[0] + '+' + str(commit) + '_' + variant.split('_')[1] + '_' + variant.split('_')[2])

    def unfmt_variant(variant):
        commit = variant.split('_')[0].split('+')[-1]
        variant_root = variant.split('_')[1] + '_' + variant.split('_')[2]
        # st.write(variant_root)
        variant_stem = variant.split('_')[0].split('+')
        variant_stem.pop()
        variant_stem = reduce(lambda a, b: b if a == "" else a + "+" + b, variant_stem, "")
        new_variant = variant_stem + '_' + variant_root
        # st.write(new_variant)
        return (commit , new_variant)
    

    def get_selected_values(n):
        lst = []
        for i in range(n):
            # create the selectbox in columns
            host_val = containers[i][0].selectbox('hostname', benches.structure.keys(), key = str(i) + '0_' + benches.config["bench_type"])
            timestamp_val = containers[i][1].selectbox('timestamp', benches.structure[host_val].keys(), key = str(i) + '1_' + benches.config["bench_type"])
            # st.write((benches.structure[host_val][timestamp_val]).items())
            if (benches.structure[host_val][timestamp_val]).items():
                commits, variants = unzip_dict((benches.structure[host_val][timestamp_val]).items())
                # st.write(variants)
                fmtted_variants = [fmt_variant(c, v) for c,v in zip(commits, variants)]
                # st.write(fmtted_variants)
                variant_val = containers[i][2].selectbox('variant', fmtted_variants, key = str(i) + '2_' + benches.config["bench_type"])
                selected_commit, selected_variant = unfmt_variant(variant_val)
                lst.append({"host" : host_val, "timestamp" : timestamp_val, "commit" : selected_commit, "variant" : selected_variant})
    
        return lst

    selected_benches = BenchStruct( "parallel", artifacts_dir, "_1.pausetimes_multicore.summary.bench")
    _ = [selected_benches.add(f["host"], f["timestamp"], f["commit"], f["variant"]) for f in get_selected_values(n)]
    selected_benches.sort()

    # Expander for showing bench files
    with st.expander("Show metadata of selected benchmarks"):
        st.write(selected_benches.structure)

    selected_files = flatten(selected_benches.to_filepath())

    def get_dataframe(file):
        # json to dataframe

        with open(file) as f:
            data = []
            for l in f:
                data.append(json.loads(l))
            df = pdjson.json_normalize(data)
        df["variant"] = fmt_variant(file)
        
        return df


    def get_dataframes_from_files(files):
        data_frames = [get_dataframe(file) for file in files]
        df = pd.concat (data_frames, sort=False)

        mdf = df.loc[df['name'].str.contains('.*multicore.*',regex=True),:]
        mdf['num_domains'] = mdf['name'].str.split('.',expand=True)[1].str.split('_',expand=True)[0]
        mdf['num_domains'] = pd.to_numeric(mdf['num_domains'])
        mdf['name'] = mdf['name'].replace('\..*?_','.',regex=True)

        mdf = mdf.drop_duplicates(subset=["name","variant", "max_latency", "num_domains"])
        mdf = mdf.sort_values(['name'])
        return mdf
    
    mdf = get_dataframes_from_files(selected_files)
    
    def plotLatencyAt(df,at):
        fdf = df.filter(["name","variant",at + "_latency","num_domains"])
        fdf.sort_values(by="name",inplace=True)
        fdf[at + "_latency"] = fdf[at + "_latency"] / 1000.0
        with sns.plotting_context(rc={"font.size":14,"axes.titlesize":14,"axes.labelsize":14,
                                    "legend.fontsize":14}):
            g = sns.relplot(x='num_domains', y = at + '_latency', hue='variant', col='name',
                            data=fdf, kind='line', style='variant', markers=True, col_wrap = 5, lw=3)
            for ax in g.axes:
                ax.set_ylabel(at + " latency (microseconds)")
                ax.set_xlabel("Number of Domains")
                ax.set_yscale('log')
            return g

    st.header("Max Latency")
    with st.expander("Expand"):
        st.write(mdf)

        max_latency_g = plotLatencyAt(mdf,"max")
        st.pyplot(max_latency_g)
    
    
    def getLatencyAt(df,percentile,idx):
        groups = df.groupby('variant')
        ndfs = []
        for group in groups:
            (v,df) = group
            count = 0
            for i, row in df.iterrows():
                count += 1
                df.at[i,percentile+"_latency"] = list(df.at[i,"distr_latency"])[idx]
            print(count)
            ndfs.append(df)
        return pd.concat(ndfs)

    mdf2 = getLatencyAt(mdf,"99.9",-1)
    st.header("99.9th Percentile Latency")
    with st.expander("Expand"):
        st.write(mdf2.filter(["name","variant","99.9_latency"]))

        g_99_9 = plotLatencyAt(mdf2,"99.9")
        st.pyplot(g_99_9)
    
    mdf3 = getLatencyAt(mdf,"99",-2)
    st.header("99th Percentile Latency")
    with st.expander("Expand"):
        st.write(mdf3.filter(["name","variant","99_latency"]))

        g_99 = plotLatencyAt(mdf3,"99")
        st.pyplot(g_99)
    
    st.header("Mean Latency")
    st.pyplot(plotLatencyAt(mdf,"mean"))