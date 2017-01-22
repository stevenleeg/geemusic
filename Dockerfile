FROM alpine:latest
MAINTAINER Spencer Julian <hellothere@spencerjulian.com>

RUN apk update \
 && apk upgrade \
 && apk add --update curl wget bash ruby ruby-bundler python python-dev py-pip dumb-init musl linux-headers build-base libffi-dev openssl-dev ruby-rdoc ruby-irb\
 && rm -rf /var/cache/apk/* \
 && mkdir /geemusic

COPY . /geemusic
WORKDIR /geemusic

RUN pip install -r requirements.txt \
 && gem install foreman

EXPOSE 4000

# Make sure to run with the GOOGLE_EMAIL, GOOGLE_PASSWORD, and APP_URL environment vars!
ENTRYPOINT ["/usr/bin/dumb-init"]
CMD ["foreman", "start"]
