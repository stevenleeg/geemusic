from flask import Flask
from flask_ask import Ask

from utils.music import GMusicWrapper

app = Flask(__name__)
ask = Ask(app, '/alexa')

api = GMusicWrapper.generate_api(logger=app.logger)

from utils.music_queue import MusicQueue

queue = MusicQueue()
import intents
import controllers
