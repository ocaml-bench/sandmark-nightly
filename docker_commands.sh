#!/bin/bash

cd $(pwd)/sandmark-nightly/ && streamlit run app/app.py & 
P1=$!
jupyterhub &
P2=$!
wait $P1 $P2