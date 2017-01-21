FROM alpine:latest
MAINTAINER Spencer Julian <hellothere@spencerjulian.com>

RUN apk update \
 && apk upgrade \
 && apk add --update curl wget bash ruby ruby-bundler python3.4 python3.4-dev \
 && easy_install pip && pip install --upgrade pip \
 && if [[ ! -e /usr/bin/pip ]]; then ln -sf /usr/bin/pip3.4 /usr/bin/pip; fi \
 && rm -rf /var/cache/apk/* \
 && mkdir /geemusic

COPY . /geemusic
WORKDIR /geemusic

RUN pip install -r requirements.txt \
 && gem install foreman

EXPOSE 4000

# Make sure to run with the GOOGLE_EMAIL, GOOGLE_PASSWORD, and APP_URL environment vars!
CMD ['foreman', 'start']
