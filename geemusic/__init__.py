from flask import Flask
from flask_ask import Ask
from utils.music_queue import MusicQueue

app = Flask(__name__)
ask = Ask(app, '/alexa')
queue = MusicQueue()

import intents
import controllers
