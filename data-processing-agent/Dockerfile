FROM java:openjdk-8-jre-alpine

RUN apk add --no-cache openssl bash

ENV DOCKERIZE_VERSION v0.4.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

COPY . /home
WORKDIR /home

RUN ln -s /config/conf.cfg ./conf.cfg

VOLUME /config
EXPOSE 8319