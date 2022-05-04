FROM python:3.10.4-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install  cron binutils -y

RUN mkdir -p /bot
RUN mkdir -p /tmp/bot

COPY . /tmp/bot/

RUN pip install --no-cache-dir -r /tmp/bot/requirements.txt
RUN cd /tmp/bot/ && pyinstaller --distpath /bot /tmp/bot/main.spec && rm -rf ./build && pyinstaller --distpath /bot /tmp/bot/single.spec

RUN pip uninstall -r /tmp/bot/requirements.txt -y
RUN cd / && rm -rf /tmp/bot


WORKDIR /bot
