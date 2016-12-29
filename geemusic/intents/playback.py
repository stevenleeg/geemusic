from flask_ask import statement, audio
from geemusic import ask

@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Pausing').stop()

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio().resume()

@ask.intent('AMAZON.StopIntent')
def resume():
    return audio('Stopping').stop()
