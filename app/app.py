import importlib

import streamlit as st

from apps.utils import write_params_to_session
from config import config
from multiapp import MultiApp

st.set_page_config(page_title="Sandmark Nightly", page_icon="🐫", layout="wide")

params = st.experimental_get_query_params()
app = MultiApp(params)

for title, data in config.items():
    name = data["module"]
    module = importlib.import_module(f"apps.{name}")
    app.add_app(title, module.app)

# The main app
params = st.experimental_get_query_params()
write_params_to_session(params)
app.run()
