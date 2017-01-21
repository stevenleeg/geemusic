FROM alpine:latest
MAINTAINER Spencer Julian <hellothere@spencerjulian.com>

RUN apk update \
 && apk upgrade \
 && apk add --update curl wget bash ruby ruby-bundler python python-dev py-pip \
 && rm -rf /var/cache/apk/* \
 && mkdir /geemusic

COPY . /geemusic

RUN pip install -r requirements.txt \
 && gem install foreman

# These don't need to be here I think, but I'm defining them for reference.
ENV GOOGLE_EMAIL
ENV GOOGLE_PASSWORD
ENV APP_URL

EXPOSE 4000

CMD ['foreman', 'start']
