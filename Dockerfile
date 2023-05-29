FROM python:3.9
EXPOSE 8501

COPY sandmark-nightly-client-crontab /etc/cron.d/sandmark-nightly-client-crontab
RUN apt-get update && apt-get -y install sudo git wget cron vim jq
RUN chmod 0644 /etc/cron.d/sandmark-nightly-client-crontab && \
    crontab /etc/cron.d/sandmark-nightly-client-crontab
WORKDIR /sandmark-nightly
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD streamlit run app/app.py
