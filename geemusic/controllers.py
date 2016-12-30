from flask import redirect
from os import environ
from geemusic import app
from geemusic.utils.music import GMusicWrapper

@app.route("/stream/<song_id>")
def redirect_to_stream(song_id):
    api = GMusicWrapper(environ['GOOGLE_EMAIL'], environ['GOOGLE_PASSWORD'])
    stream_url = api.get_google_stream_url(song_id)

    app.logger.debug('URL is %s' % stream_url)

    return redirect(stream_url, code=302)
