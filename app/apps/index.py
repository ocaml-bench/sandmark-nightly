import streamlit as st

def app():
    st.title("Welcome to Sandmark Nightly")
    st.markdown('''
        #### There are 4 different sets of benchmarks present in the nightly runs
        - Sequential Benchmarks : 
            - Variants : 
                - OCaml 5.0+trunk
                - OCaml 5.0+domains
            - Metrics :
                - Time
                - Top Heap Words
                - Max RSS (in kB)
                - Major Collections
                - Minor Collections
    
        - Parallel Benchmarks :
            - Variants :
                - OCaml 5.0+domains
            - Metrics :
                - Speedup

        - Instrumented Pausetimes (sequential) : 
            The instrumented pausetimes are not updated currently
            - Past :
                - Variants :
                    - OCaml 4.12.0+stock+instrumented
                    - OCaml 4.12.0+domains+effects+instrumented
                - Metrics :
                    - Max Latency
                    - 99.9th Percentile Latency
                    - 99th Precentile Latency

        - Instrumented Pausetimes (parallel) : 
            The instrumented pausetimes are not updated currently
            - Past :
                - Variants :
                    - OCaml 4.12.0+domains+effects+instrumented
                - Metrics :
                    - Max Latency
                    - 99.9th Percentile Latency
                    - 99th Perecentile Latency
                    - Mean Latency
    ''')