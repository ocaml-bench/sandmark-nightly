from pandas.core.frame import DataFrame
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

def app():
	st.title("Sequential Benchmarks")

	# Problem : right now the structure is a nested dict of
	#     `(hostname * (timestamp * (variants list)) dict ) dict`
	# and this nested structure although works but it is a bit difficult to work with
	# so we need to create a class object which is a record type and add functions to 

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

	current = os.getcwd().split('/')
	current.pop()
	artifacts_dir = '/'.join(current) + '/sandmark-nightly'
	# print(artifacts_dir)
	benches = benchstruct.BenchStruct("sequential", artifacts_dir, "_1.orun.summary.bench")
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
		commit_variant_tuple_lst = [(x1, x2) for x1, x2 in zip(a[0], a[1])]
		return commit_variant_tuple_lst

	def fmt_variant(commit, variant_lst):
		# st.write(commit)
		# st.write(variant)
		def fmt(commit, variant):
			variant_name = variant.split('_')[0]
			commit_id = str(commit)
			variant_tail = variant.split('_')[1]
			return (variant.split('_')[0] + '+' + str(commit) + '_' + variant.split('_')[1])
		fmt_variant_lst = [fmt(commit, v) for v in variant_lst]
		return fmt_variant_lst


	def unfmt_variant(variant):
		commit = variant.split('_')[0].split('+')[-1]
		variant_root = variant.split('_')[1]
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
			# st.write(benches.structure)
			commit_variant_tuple_lst = unzip_dict((benches.structure[host_val][timestamp_val]).items())
			fmtted_variants = [fmt_variant(c, v) for c,v in commit_variant_tuple_lst]
			# st.write("formatted variants")
			# st.write(fmtted_variants)
			fmtted_variants = flatten(fmtted_variants)
			variant_val = containers[i][2].selectbox('variant', fmtted_variants, key = str(i) + '2_' + benches.config["bench_type"])
			selected_commit, selected_variant = unfmt_variant(variant_val)
			lst.append({"host" : host_val, "timestamp" : timestamp_val, "commit" : selected_commit, "variant" : selected_variant})
		return lst

	selected_benches = benchstruct.BenchStruct("sequential", artifacts_dir, "_1.orun.summary.bench")
	_ = [selected_benches.add(f["host"], f["timestamp"], f["commit"], f["variant"]) for f in get_selected_values(n)]
	selected_benches.sort()

	# Expander for showing bench files
	with st.expander("Show metadata of selected benchmarks"):
		st.write(selected_benches.structure)

	selected_files = flatten(selected_benches.to_filepath())

	def dataframe_intersection(data_frames):
		intersection_set_list = [set(df['name']) for df in data_frames]
		list_diff = list(reduce(lambda x, y: x.intersection(y), intersection_set_list))
		new_data_frames = []
		for elem in list_diff:
			for df in data_frames:
				new_data_frames.append(df[(df.name == elem)])
		list_diff.sort()
		# st.write(list_diff)
		return new_data_frames

	def get_dataframe(file):
		# json to dataframe
		# st.write(file)
		with open(file) as f:
			data = []
			for l in f:
				temp = json.loads(l)
				#check if the benchmark json contains name field
				#avoids crashing if the entry doesn't contain a benchmark
				if 'name' in temp:
					data.append(temp)
			df = pd.json_normalize(data)
			value     = file.split('/' + benches.config["bench_type"] + '/')[1]
			date      = value.split('/')[1].split('_')[0]
			commit_id = value.split('/')[2][:7]
			variant   = value.split('/')[3].split('_')[0]
			df["variant"] = variant + '_' + date + '_' + commit_id
		return df



	def get_dataframes_from_files(files):
		data_frames = [get_dataframe(file) for file in files]
		new_data_frames = dataframe_intersection(data_frames=data_frames)
		df = pd.concat(new_data_frames, sort=False)
		# st.write(df)
		df.sort_values(['name'])
		return df

	def plot(df, y_axis):
		graph = sns.catplot (
			x = "name",
			y = y_axis,
			hue = "variant",
			data = df,
			kind = "bar",
			aspect = 4
		)
		graph.set_xticklabels(rotation=90)
		return graph

	def fmt_baseline(record):
		date = record["timestamp"].split('_')[0]
		commit = record["commit"][:7]
		variant = record["variant"].split('_')[0]
		s = str(variant) + '_' + date + '_' + commit
		return s

	def create_column(df, variant, metric):
		df = pd.DataFrame.copy(df)
		variant_metric_name = list([ zip(df[metric], df[x], df['name'])
				for x in df.columns.array if x == "variant" ][0])
		# st.write(df)
		# st.write(variant)
		name_metric = {n:t for (t, v, n) in variant_metric_name if v == variant}
		return name_metric

	def add_display_name(df,variant, metric):
		name_metric = create_column(pd.DataFrame.copy(df), variant, metric)
		disp_name = [name+" ("+str(round(name_metric[name], 2))+")" for name in df["name"]]
		df["display_name"] = pd.Series(disp_name, index=df.index)
		return df

	def normalise(df,variant,topic,additionalTopics=[]):
		df = add_display_name(df,variant,topic)
		df = df.sort_values(["name","variant"])
		grouped = df.filter(items=['name',topic,'variant','display_name']+additionalTopics).groupby('variant')
		ndata_frames = []
		# st.write(grouped)
		for group in grouped:
			(v,data) = group
			if(v != variant):
				data['b'+topic] = grouped.get_group(variant)[topic].values
				data[['n'+topic]] = data[[topic]].div(grouped.get_group(variant)[topic].values, axis=0)
				for t in additionalTopics:
					data[[t]] = grouped.get_group(variant)[t].values
				ndata_frames.append(data)
				# st.write(data)
			else:
				continue
		if ndata_frames :
			df = pd.concat(ndata_frames)
			return df
		else:
			st.warning("Variants selected are the same, please select different variants to generate a normalized graph")
			return pd.DataFrame()

	def plot_normalised(baseline, df, topic):
		xlabel = "Benchmarks (baseline = " + baseline + ")"
		if not df.empty:
			df = pd.DataFrame.copy(df)
			df.sort_values(by=[topic],inplace=True)
			df[topic] = df[topic] - 1
			g = sns.catplot (x="display_name", y=topic, hue='variant', data = df, kind ='bar', aspect=4, bottom=1)
			g.set_xticklabels(rotation=90)
			g.ax.legend(loc=8)
			g._legend.remove()
			g.ax.set_xlabel(xlabel)
			return g
	
	df = get_dataframes_from_files(selected_files)
	# df = df.drop_duplicates(subset=['name','variant'])


	st.header("Select baseline (for normalized graphs)")
	baseline_container = st.columns(3)
	baseline_host = baseline_container[0].selectbox(
		'hostname', 
		selected_benches.structure.keys(),
		key = 'B0_' + benches.config["bench_type"])
	baseline_timestamp = baseline_container[1].selectbox(
		'timestamp', 
		selected_benches.structure[baseline_host].keys(),
		key = 'B1_' + benches.config["bench_type"])    
	baseline_commit_variants_tuples_lst = unzip_dict((selected_benches.structure[baseline_host][baseline_timestamp]).items())

	fmtted_variants = [fmt_variant(c, v) for c,v in baseline_commit_variants_tuples_lst]
	fmtted_variants = set(flatten(fmtted_variants))
	# st.write(fmtted_variants)
	variant_val = baseline_container[2].selectbox('variant', fmtted_variants, key = 'B2_' + benches.config["bench_type"])
	baseline_commit, baseline_variant = unfmt_variant(variant_val)

	baseline_record = {
		"host" : baseline_host,
		"timestamp" : baseline_timestamp,
		"commit" : baseline_commit,
		"variant" : baseline_variant
	}


	# FIXME : coq fails to build on domains
	# df = df[(df.name != 'coq.BasicSyntax.v') & (df.name != 'coq.AbstractInterpretation.v')]

	baseline = fmt_baseline(baseline_record)

	# Display Components

	st.header("Time")
	with st.expander("Data"):
		st.write(df)
	with st.expander("Graph"):
		st.pyplot(plot(df.copy(), 'time_secs'))

	ndf = normalise(df.copy(), baseline, 'time_secs')
	st.header("Normalized Time")
	with st.expander("Data"):
		st.write(ndf)
	with st.expander("Graph"):
		g = plot_normalised(baseline, ndf,'ntime_secs')
		st.pyplot(g)

	st.header("Top heap words")
	with st.expander("Data"):
		st.write(df)
	with st.expander("Graph"):
		st.pyplot(plot(df.copy(), 'gc.top_heap_words'))
	ndf = normalise(df.copy(), baseline, 'gc.top_heap_words')
	st.header("Normalized top heap words")
	with st.expander("Data"):
		st.write(ndf)
	with st.expander("Graph"):
		g = plot_normalised(baseline, ndf, 'ngc.top_heap_words')
		st.pyplot(g)

	st.header("Max RSS (KB)")
	with st.expander("Data"):
		st.write(df)
	with st.expander("Graph"):
		st.pyplot(plot(df.copy(), "maxrss_kB"))
	ndf = normalise(df.copy(), baseline, 'maxrss_kB')
	st.header("Normalized Max RSS (KB)")
	with st.expander("Data"):
		st.write(ndf)
	with st.expander("Graph"):
		g = plot_normalised(baseline, ndf, 'nmaxrss_kB')
		st.pyplot(g)

	st.header("Major Collections")
	with st.expander("Data"):
		st.write(df)
	with st.expander("Graph"):
		st.pyplot(plot(df.copy(), "gc.major_collections"))
	ndf = normalise(df.copy(), baseline, 'gc.major_collections')
	st.header("Normalized major collections")
	with st.expander("Data"):
		st.write(ndf)
	with st.expander("Graph"):
		g = plot_normalised(baseline, ndf, 'ngc.major_collections')
		st.pyplot(g)

	st.header("Minor Collections")
	with st.expander("Data"):
		st.write(df)
	with st.expander("Graph"):
		st.pyplot(plot(df.copy(), "gc.minor_collections"))
	ndf = normalise(df.copy(), baseline, 'gc.minor_collections')
	st.header("Normalized minor collections")
	with st.expander("Data"):
		st.write(ndf)
	with st.expander("Graph"):
		g = plot_normalised(baseline, ndf, 'ngc.minor_collections')
		st.pyplot(g)