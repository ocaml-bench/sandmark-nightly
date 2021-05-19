#!/bin/bash

#TOKEN required for automatic commit to sandmark-nightly repo
#To generate the token use the following tutorial link
#https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
TOKEN=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

#check if sandmark and sandmark-nightly repo exist in the default or custom SANDMARK_NIGHTLY_DIR
function check_sandmark_subdir {
	if [ ! -d $1/sandmark-nightly ]; then
		git clone https://$TOKEN@github.com/shubhamkumar13/sandmark-nightly.git $1/sandmark-nightly
	fi;
	if [ ! -d $1/sandmark ]; then
		git clone https://github.com/ocaml-bench/sandmark.git $1/sandmark
	fi;
}

#if nothing specified then default sandmark directory
SANDMARK_NIGHTLY_DIR=${SANDMARK_NIGHTLY_DIR:-"$HOME/sandmark_nightly_workspace"}
if [ ! -d $SANDMARK_NIGHTLY_DIR ]; then 
	mkdir $SANDMARK_NIGHTLY_DIR
fi;

check_sandmark_subdir $SANDMARK_NIGHTLY_DIR

#initialize the date and time and create sequential and parallel directories
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP
mkdir -p $SANDMARK_NIGHTLY_DIR/sandmark-nightly/parallel/$TIMESTAMP

#get the latest sandmark pull
cd $SANDMARK_NIGHTLY_DIR/sandmark/
git pull origin master
make clean

#sequential benchmarks
TAG='"macro_bench"' make run_config_filtered.json
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+stock.bench
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+domains+effects.bench

cp -a $SANDMARK_NIGHTLY_DIR/sandmark/_results/*.bench $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP
rm -rf _results/

#parallel benchmarks
TAG='"macro_bench"' make multicore_parallel_run_config_filtered.json
RUN_BENCH_TARGET=run_orunchrt \
	BUILD_BENCH_TARGET=multibench_parallel \
	RUN_CONFIG_JSON=multicore_parallel_run_config_filtered.json \
	make ocaml-versions/4.12.0+domains.bench

RUN_BENCH_TARGET=run_orunchrt \
	BUILD_BENCH_TARGET=multibench_parallel \
	RUN_CONFIG_JSON=multicore_parallel_run_config_filtered.json \
	make ocaml-versions/4.12.0+domains+effects.bench

cp -a $SANDMARK_NIGHTLY_DIR/sandmark/_results/*.bench $SANDMARK_NIGHTLY_DIR/sandmark-nightly/parallel/$TIMESTAMP
rm -rf _results/

#push to sandmark-nightly
cd $SANDMARK_NIGHTLY_DIR/sandmark-nightly
git pull
git add .
git commit -m "this is an automated commit"
git push
