from __future__ import absolute_import
from flask import Flask
from flask_ask import Ask
from os import environ
import logging

from .utils.music import GMusicWrapper
from .utils.music_queue import MusicQueue

app = Flask(__name__)
ask = Ask(app, '/alexa')

if str(environ['DEBUG_MODE']) is True:
    logLevel = logging.DEBUG
else:
    logLevel = logging.INFO

logging.getLogger("flask_ask").setLevel(logLevel)

api = GMusicWrapper.generate_api(logger=app.logger)
queue = MusicQueue(api)

from . import intents
from . import controllers
