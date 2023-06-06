# sandmark-nightly

This repository contains results from the nightly runs of
[Sandmark](https://github.com/ocaml-bench/sandmark), and a [Streamlit
app](https://sandmark.tarides.com/) to visualize the results.

# How to run the webapp locally

```bash
$ git clone https://github.com/ocaml-bench/sandmark-nightly.git
$ cd sandmark-nightly
$ docker build -t sandmark-nightly . -f Dockerfile
$ docker run -p 8501:8501 sandmark-nightly
```
The app will be available at `http://localhost:8501`

# How to run the app on Streamlit Cloud

It is possible to run a specific version (branch) of the code on the Streamlit
Cloud.  This is useful to easily deploy specific branches of pull requests for
reviews, etc.  It's easiest to deploy branches from your own fork to the
Streamlit Cloud, and the steps below assume you are doing so.


1. Login to the [Streamlit Cloud](https://share.streamlit.io/). It's possible
   to login using your Google/GitHub account.
2. Click the "New App" button.
3. Fill the repository to your fork, for example `punchagan/sandmark`.
4. Fill in the name of the branch.
5. Set the main file path to `app/app.py`.
6. Deploy!
