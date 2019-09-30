FROM python:3.7-alpine as python-base
MAINTAINER Spencer Julian <hellothere@spencerjulian.com>
RUN apk add --no-cache --update curl wget build-base libffi-dev openssl-dev 
COPY requirements.txt /tmp
RUN pip install -U 'pip<10'
RUN pip wheel --wheel-dir=/root/wheels -r /tmp/requirements.txt

FROM python:3.7-alpine
COPY --from=python-base /root/wheels /root/wheels
RUN apk --no-cache add --update ruby ruby-bundler ruby-rdoc libffi openssl && \
gem install foreman && \
pip install -U 'pip<10' && \
pip install --no-index --find-links=/root/wheels /root/wheels/* && \
rm -rf /root/wheels

COPY . /geemusic
WORKDIR /geemusic

EXPOSE 5000

# Make sure to run with the GOOGLE_EMAIL, GOOGLE_PASSWORD, and APP_URL environment vars!
CMD ["foreman", "start"]
