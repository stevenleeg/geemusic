from flask import Flask
from flask_ask import Ask
from utils.music_queue import MusicQueue
from utils.music import GMusicWrapper

app = Flask(__name__)
ask = Ask(app, '/alexa')

queue = MusicQueue()
api = GMusicWrapper.generate_api()

import intents
import controllers
