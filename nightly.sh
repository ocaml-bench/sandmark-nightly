#!/bin/bash

#add local path to crontab path
#PATH=$PATH:/home/shubham/.local/bin:/home/shubham/.opam/4.10.0+multicore/bin:/home/shubham/.local/bin:/home/shubham/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

#initialize the date and time and create sequential and parallel directories
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p /home/shubham/sandmark-nightly/sequential/$timestamp
mkdir -p /home/shubham/sandmark-nightly/parallel/$timestamp

#get the latest sandmark pull
cd /home/shubham/sandmark/
git pull origin master
make clean

#sequential benchmarks
TAG='"macro_bench"' make run_config_filtered.json
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+stock.bench
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+domains+effects.bench

cp -a /home/shubham/sandmark/_results/*.bench /home/shubham/sandmark-nightly/sequential/$timestamp
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

cp -a /home/shubham/sandmark/_results/*.bench /home/shubham/sandmark-nightly/parallel/$timestamp
rm -rf _results/

#push to sandmark-nightly
cd /home/shubham/sandmark-nightly
git add .
git commit -m "this is an automated commit"
git push