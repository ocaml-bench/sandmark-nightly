#!/bin/bash

papermill sequential_nightly.ipynb sequential_nightly_turing.ipynb -f parameters_turing.yaml
papermill parallel_nightly.ipynb parallel_nightly_turing.ipynb -f parameters_turing.yaml
papermill sequential_nightly.ipynb sequential_nightly_navajo.ipynb -f parameters_navajo.yaml
papermill parallel_nightly.ipynb parallel_nightly_navajo.ipynb -f parameters_navajo.yaml
jupyter nbconvert --to html sequential_nightly_turing.ipynb 
jupyter nbconvert --to html sequential_nightly_navajo.ipynb 
jupyter nbconvert --to html parallel_nightly_turing.ipynb 
jupyter nbconvert --to html parallel_nightly_navajo.ipynb 
mv *.html ../static-html-pages/
rm *_turing.ipynb && rm *_navajo.ipynb 
