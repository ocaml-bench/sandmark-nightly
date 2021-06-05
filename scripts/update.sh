#!/bin/bash

cd /srv/data/sandmark-nightly
git pull

sudo cp /srv/data/sandmark-nightly/notebooks/*.ipynb /etc/skel/

IN=$(grep 'jupyterhub-users' /etc/group)

IFS=':' read -ra TEMP <<< "$IN"

IFS=',' read -ra USERS <<< "${TEMP[3]}"

for i in "${USERS[@]}"; do
    sudo cp -a /etc/skel/*.ipynb /home/$i
done
