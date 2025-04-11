FROM python:latest

LABEL authors="thorhsu"
USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y software-properties-common openssh-client build-essential libfreetype-dev libfreetype6 libfreetype6-dev nfs-common

RUN apt-get -y install cron libaio1 libaio-dev
RUN apt-get -y install tzdata git curl vim unzip

RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

ENV PYTHONUNBUFFERED 1
RUN mkdir /docker

COPY init.sql /docker-entrypoint-initdb.d/init.sql


RUN mkdir /app

COPY . /app


RUN rm -f /app/settings/env_dev.json
RUN rm -f /app/init.sql
RUN curl -fL https://download.oracle.com/otn_software/linux/instantclient/2370000/instantclient-basic-linux.x64-23.7.0.25.01.zip -o instantclient.zip 
RUN mkdir -p /opt/odb
RUN unzip instantclient.zip -d /opt/odb
RUN rm -f instantclient.zip 

ENV ORACLE_HOME="/opt/odb/instantclient_23_7"
ENV LD_LIBRARY_PATH="$ORACLE_HOME:$LD_LIBRARY_PATH"
ENV TNS_ADMIN="$ORACLE_HOME/network/admin"
ENV PATH="$ORACLE_HOME:$PATH"

# RUN rm -rf /app/sfp/*
RUN rm -rf /var/run/crond.pid
RUN mkdir -p "/var/run"

RUN mkdir -p "/etc/cron.d"
COPY crontab /etc/cron.d/crontab
# Copy crontab file and set permissions
RUN chmod 0644 /etc/cron.d/crontab

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/share
RUN mkdir -p /app/share/log/
RUN mkdir -p /app/share/files4parse/
RUN touch /app/share/log/cron.log
#RUN crontab /etc/cron.d/crontab
# Start cron when the container starts
CMD cron && tail -f /app/share/log/cron.log
