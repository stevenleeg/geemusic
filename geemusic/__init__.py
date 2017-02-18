from __future__ import absolute_import
from flask import Flask
from flask_ask import Ask
import logging

from .utils.music import GMusicWrapper
from .utils.music_queue import MusicQueue

app = Flask(__name__)
ask = Ask(app, '/alexa')
logging.getLogger("flask_ask").setLevel(logging.INFO)

api = GMusicWrapper.generate_api(logger=app.logger)
queue = MusicQueue(api)

from . import intents
from . import controllers
