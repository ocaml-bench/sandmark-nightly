# sandmark-nightly

Stores nightly runs of sandmark

# How to run the webapp locally

```bash
$ git clone https://github.com/ocaml-bench/sandmark-nightly.git
$ cd sandmark-nightly
$ docker build -t sandmark-nightly . -f Dockerfile
$ docker run -p 8501:8501 sandmark-nightly
```
The app will be available at `http://localhost:8501`
