import streamlit as st
from multiapp import MultiApp
from apps import index, sequential_benchmarks, parallel_benchmarks, instrumented_pausetimes_sequential, instrumented_pausetimes_parallel # import your app modules here

st.set_page_config(
    page_title="Sandmark Nightly",
    page_icon="🐫",
    layout="wide"
)

app = MultiApp()

# Add all your application here
app.add_app("Home", index.app)
app.add_app("Sequential Benchmarks", sequential_benchmarks.app)
app.add_app("Parallel Benchmarks", parallel_benchmarks.app)
#app.add_app("Instrumented Pausetimes Sequential", instrumented_pausetimes_sequential.app)
#app.add_app("Instrumented Pausetimes Parallel", instrumented_pausetimes_parallel.app)

# The main app
app.run()
