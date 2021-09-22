FROM jupyterhub/jupyterhub:1.4.2

COPY scripts/setup_aws.sh /srv/jupyterhub/
COPY docker_commands.sh /srv/jupyterhub/

RUN apt-get update && apt-get -y install sudo git supervisor
RUN pip install --no-cache-dir streamlit nested_dict seaborn multipledispatch jupyterhub
RUN bash /srv/jupyterhub/setup_aws.sh
RUN useradd -ms /bin/bash admin
RUN echo 'admin:admin' | chpasswd

EXPOSE 8000
EXPOSE 8501

COPY docker_commands.sh /srv/jupyterhub
RUN chmod +x /srv/jupyterhub/docker_commands.sh
ENTRYPOINT [ "/srv/jupyterhub/docker_commands.sh" ]