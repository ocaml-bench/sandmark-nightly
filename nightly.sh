#!/bin/bash

#add local path to crontab path
#PATH=$PATH:/home/shubham/.local/bin:/home/shubham/.opam/4.10.0+multicore/bin:/home/shubham/.local/bin:/home/shubham/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

#TOKEN required for automatic commit to sandmark-nightly repo
TOKEN=${TOKEN:-""}

#check if sandmark and sandmark-nightly repo exist in the default or custom SANDMARK_NIGHTLY_DIR
function check_sandmark_subdir {
	if [ $(find $1 -name "sandmark-nightly" | wc -l) -lt 1 ]; then
		git clone https://$TOKEN@github.com/shubhamkumar13/sandmark-nightly.git $1/
	fi;
	if [ $(find $1 -name "sandmark" | wc -l) -lt 1 ]; then
		git clone https://github.com/ocaml-bench/sandmark.git $1/
	fi;
}

#if nothing specified then default sandmark directory
SANDMARK_NIGHTLY_DIR=${SANDMARK_NIGHTLY_DIR:-""}
if [ ! -z $SANDMARK_NIGHTLY_DIR ]; then 
	mkdir -p $(HOME)/sandmark_nightly_workspace && SANDMARK_NIGHTLY_DIR=$(HOME)/sandmark_nightly_workspace
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
git add .
git commit -m "this is an automated commit"
git push