FROM python:3.9
EXPOSE 8501

COPY sandmark-nightly-client-crontab /etc/cron.d/sandmark-nightly-client-crontab
RUN apt-get update && apt-get -y install sudo git wget cron vim && \
    pip install --no-cache-dir streamlit nested_dict seaborn
RUN pip install -U click==8
RUN chmod 0644 /etc/cron.d/sandmark-nightly-client-crontab && \
    crontab /etc/cron.d/sandmark-nightly-client-crontab
WORKDIR /sandmark-nightly
COPY . .
CMD streamlit run app/app.py
