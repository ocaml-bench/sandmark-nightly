#!/bin/bash
#Check if SKEL=/etc/skel in /etc/default/useradd is uncommented and then proceed to execute the bash script

#pip3 install nested_dict pandas seaborn

git clone https://github.com/ocaml-bench/sandmark-nightly.git

mkdir -p /srv/data/
cp -a $(pwd)/sandmark-nightly /srv/data

ln -s /srv/data/sandmark-nightly/ /etc/skel/sandmark-nightly

cp /srv/data/sandmark-nightly/notebooks/*.ipynb /etc/skel

cp $(pwd)/sandmark-nightly/scripts/update.sh .

chmod +x update.sh

bash update.sh
