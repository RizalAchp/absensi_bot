FROM python:3.10-slim-bullseye

RUN apt-get update
RUN apt-get install build-essential cron -y

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY src/* .
COPY bin/* /usr/bin/
# CMD [ "python", "-i", "./main", "setup" ]
# RUN crontab ./mycrontab
