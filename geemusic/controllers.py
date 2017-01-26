from flask import redirect
from os import environ
from geemusic import app, api
from geemusic.utils.music import GMusicWrapper

@app.route("/stream/<song_id>")
def redirect_to_stream(song_id):
    stream_url = api.get_google_stream_url(song_id)
    # Scrobble if Last.fm is setup
    if environ['LAST_FM_ACTIVE']:
        last_fm.execute(song_id)

    app.logger.debug('URL is %s' % stream_url)

    return redirect(stream_url, code=302)
