# sandmark-nightly
Stores nightly runs of sandmark

# How to setup on an AWS machine

1. Use the AWS setup tutorial mentioned in the [TLJH documentation](https://tljh.jupyter.org/en/latest/install/amazon.html).
2. Check the `SKEL` variable in `/etc/default/useradd` to be uncommented and it should be assigned to `/etc/skel` and it should end up looking like `SKEL=/etc/skel`.
3. Start the JupyterHub server on the aws machine which is currently empty.
4. Then open the terminal and download the setup script using `wget https://raw.githubusercontent.com/shubhamkumar13/sandmark-nightly/main/scripts/setup_aws.sh`.
5. Run the script from the terminal with `bash setup_aws.sh`.

# How to run the webapp locally
1. Install [streamlit](https://docs.streamlit.io/en/stable/installation.html)
2. Clone the repo `git clone https://github.com/ocaml-bench/sandmark-nightly.git` and `cd sandmark-nightly`
3. When inside the repo directory run `streamlit run app/app.py` the app should ideally be now hosted at `localhost:8501`