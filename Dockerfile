FROM alpine:latest
MAINTAINER Spencer Julian <hellothere@spencerjulian.com>

ENV BUILD_DEPS "build-base musl"

RUN apk add --no-cache $BUILD_DEPS \
  curl wget bash ruby ruby-bundler python3 py3-pip dumb-init openssl-dev \
  libffi-dev python3-dev linux-headers ruby-rdoc ruby-irb git \
  && mkdir /geemusic

COPY . /geemusic
WORKDIR /geemusic

RUN pip3 install -r requirements.txt \
 && gem install foreman

RUN apk del $BUILD_DEPS && \
  rm -rf /var/cache/apk/*

EXPOSE 5000

# Make sure to run with the GOOGLE_EMAIL, GOOGLE_PASSWORD, and APP_URL environment vars!
ENTRYPOINT ["/usr/bin/dumb-init"]
CMD ["foreman", "start"]
