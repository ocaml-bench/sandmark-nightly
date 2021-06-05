#!/bin/bash
#Check if SKEL=/etc/skel in /etc/default/useradd is uncommented and then proceed to execute the bash script

sudo -E pip install nested_dict pandas seaborn

git clone https://github.com/shubhamkumar13/sandmark-nightly.git

sudo mkdir -p /srv/data/
sudo cp -a sandmark-nightly /srv/data

sudo ln -s /srv/data/sandmark-nightly/ /etc/skel/sandmark-nightly

sudo cp /srv/data/sandmark-nightly/notebooks/*.ipynb /etc/skel

cp sandmark-nightly/scripts/update.sh .

chmod +x update.sh

bash update.sh