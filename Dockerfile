# Systemd inside a Docker container, for CI only
FROM ubuntu:20.04

RUN apt-get update --yes

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

RUN apt-get install --yes systemd curl git sudo python3 python3-dev wget python3-pip

# Kill all the things we don't need
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -exec rm \{} \;

RUN mkdir -p /etc/sudoers.d

RUN systemctl set-default multi-user.target

STOPSIGNAL SIGRTMIN+3

# Uncomment these lines for a development install
#ENV TLJH_BOOTSTRAP_DEV=yes
#ENV TLJH_BOOTSTRAP_PIP_SPEC=/srv/src
#ENV PATH=/opt/tljh/hub/bin:${PATH}

COPY scripts/setup_aws.sh /tmp/setup_aws.sh

RUN bash /tmp/setup_aws.sh

RUN wget https://raw.githubusercontent.com/jupyterhub/the-littlest-jupyterhub/master/bootstrap/bootstrap.py

RUN python3 bootstrap.py --admin admin

SHELL ["/bin/bash", "-c"]

RUN ln -s /lib/systemd/systemd /sbin/init

CMD exec /sbin/init --log-target=journal 3>&1
