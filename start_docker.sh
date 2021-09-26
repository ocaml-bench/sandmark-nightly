#!/bin/bash

docker build -t sandmark-nightly . -f Dockerfile
docker run -p 8501:8501 sandmark-nightly
