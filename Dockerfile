FROM python:3.9
EXPOSE 8501
RUN apt-get update && apt-get -y install sudo git wget vim jq
WORKDIR /sandmark-nightly
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "app/app.py"]
