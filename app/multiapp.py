"""Frameworks for running multiple Streamlit applications as a single app.
   forked from git@github.com:upraneelnihar/streamlit-multiapps.git
   Thanks to https://github.com/upraneelnihar
"""
import streamlit as st

from apps.utils import set_params_from_session


class MultiApp:
    """Framework for combining multiple streamlit applications.
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """

    def __init__(self, params):
        self.apps = []
        self.params = params

    def add_app(self, slug, title, func):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        slug:
            slug of the app. Appears in the url query params
        """
        self.apps.append({"title": title, "function": func, "slug": slug})

    def run(self):
        state_app = st.session_state.get("app", [""])
        if isinstance(state_app, list):
            for app in self.apps:
                if app["slug"] == state_app[0]:
                    st.session_state["app"] = app
                    break

        app = st.sidebar.radio(
            "Go To",
            options=self.apps,
            format_func=lambda app: app["title"],
            key="app",
            on_change=set_params_from_session,
        )

        app["function"]()
