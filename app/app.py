import streamlit as st

from apps import (
    index,
    instrumented_pausetimes_sequential,
    parallel_benchmarks,
    perfstat,
    sequential_benchmarks,
)
from apps.utils import write_params_to_session
from multiapp import MultiApp

st.set_page_config(page_title="Sandmark Nightly", page_icon="🐫", layout="wide")

params = st.experimental_get_query_params()
app = MultiApp(params)

# Add all your application here
app.add_app("Home", index.app)
app.add_app("Sequential Benchmarks", sequential_benchmarks.app)
app.add_app("Parallel Benchmarks", parallel_benchmarks.app)
app.add_app("Perfstat Output", perfstat.app)
app.add_app("Instrumented Pausetimes Sequential", instrumented_pausetimes_sequential.app)
# app.add_app("Instrumented Pausetimes Parallel", instrumented_pausetimes_parallel.app)

# The main app
params = st.experimental_get_query_params()
write_params_to_session(params)
app.run()
