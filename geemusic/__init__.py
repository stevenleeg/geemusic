from __future__ import absolute_import
from flask import Flask
from flask_ask import Ask

from .utils.music import GMusicWrapper
from .utils.music_queue import MusicQueue

app = Flask(__name__)
ask = Ask(app, '/alexa')

api = GMusicWrapper.generate_api(logger=app.logger)
queue = MusicQueue(api)

from . import intents
from . import controllers
