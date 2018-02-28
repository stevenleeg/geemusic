from __future__ import absolute_import
from flask import Flask
from flask_ask import Ask
from os import getenv
import logging

from .utils.music import GMusicWrapper
from .utils.music_queue import MusicQueue

# Use English as default when no
# LANGUAGE env is found.
language = getenv('LANGUAGE', 'en')
    
TEMPLATE_DIR = "templates/" + language + ".yaml"
    
app = Flask(__name__)
ask = Ask(app, '/alexa', path=TEMPLATE_DIR)

if str(getenv('DEBUG_MODE')) is True:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.getLogger("flask_ask").setLevel(log_level)

api = GMusicWrapper.generate_api(logger=app.logger)
queue = MusicQueue(api)

from . import intents
from . import controllers
