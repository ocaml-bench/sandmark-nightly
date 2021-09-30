#!/bin/bash

# Install dependencies
pip3 install streamlit seaborn multipledispatch nested_dict
git clone https://github.com/ocaml-bench/sandmark-nightly.git
cd sandmark-nightly

# add cronjob
sudo cp -a sandmark-nightly-client-crontab /etc/cron.d/sandmark-nightly-client-crontab
sudo chmod 0644 /etc/cron.d/sandmark-nightly-client-crontab
crontab /etc/cron.d/sandmark-nightly-client-crontab

# run the app
streamlit run app/app.py
