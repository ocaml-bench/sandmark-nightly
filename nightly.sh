#!/bin/bash

#TOKEN required for automatic commit to sandmark-nightly repo
#To generate the token use the following tutorial link
#https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
TOKEN=${TOKEN:-""}

#git urls of ocaml 4.12.0, ocaml 4.12+domains+effects, ocaml 4.12+domains
OCAML_412_DOMAINS_EFFECTS="https://github.com/ocaml-multicore/ocaml-multicore.git refs/heads/4.12+domains+effects"
OCAML_412_STOCK="https://github.com/ocaml/ocaml.git refs/heads/4.12"

#replace urls with latest commit id
function get_latest_commit {
    get_commit=( $(eval "$1") )
    echo "${get_commit[0]}"
}

OCAML_412_DOMAINS_EFFECTS=$(get_latest_commit "git ls-remote $OCAML_412_DOMAINS_EFFECTS")
OCAML_412_STOCK=$(get_latest_commit "git ls-remote $OCAML_412_STOCK")

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
mkdir -p $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP/$OCAML_412_DOMAINS_EFFECTS
mkdir -p $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP/$OCAML_412_STOCK
mkdir -p $SANDMARK_NIGHTLY_DIR/sandmark-nightly/parallel/$TIMESTAMP/$OCAML_412_DOMAINS_EFFECTS

#get the latest sandmark pull
cd $SANDMARK_NIGHTLY_DIR/sandmark/
git pull origin master
make clean
eval $(opam env)

#sequential benchmarks
TAG='"macro_bench"' make run_config_filtered.json
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+stock.bench
RUN_CONFIG_JSON=run_config_filtered.json make ocaml-versions/4.12.0+domains+effects.bench

cp -a $SANDMARK_NIGHTLY_DIR/sandmark/_results/4.12.0+domains+effects_1.orun.summary.bench $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP/$OCAML_412_DOMAINS_EFFECTS
cp -a $SANDMARK_NIGHTLY_DIR/sandmark/_results/4.12.0+stock_1.orun.summary.bench $SANDMARK_NIGHTLY_DIR/sandmark-nightly/sequential/$TIMESTAMP/$OCAML_412_STOCK
rm -rf _results/

#parallel benchmarks
TAG='"macro_bench"' make multicore_parallel_run_config_filtered.json

RUN_BENCH_TARGET=run_orunchrt \
	BUILD_BENCH_TARGET=multibench_parallel \
	RUN_CONFIG_JSON=multicore_parallel_run_config_filtered.json \
	make ocaml-versions/4.12.0+domains+effects.bench

cp -a $SANDMARK_NIGHTLY_DIR/sandmark/_results/4.12.0+domains+effects_1.orunchrt.summary.bench $SANDMARK_NIGHTLY_DIR/sandmark-nightly/parallel/$TIMESTAMP/$OCAML_412_DOMAINS_EFFECTS
rm -rf _results/

#push to sandmark-nightly
cd $SANDMARK_NIGHTLY_DIR/sandmark-nightly
git pull
git add .
git commit -m "this is an automated commit"
git push
