from flask import redirect
from os import environ
from geemusic import app, api
from geemusic.utils.music import GMusicWrapper

@app.route("/stream/<song_id>")
def redirect_to_stream(song_id):
    stream_url = api.get_google_stream_url(song_id)
    # Scrobble if Last.fm is setup
    if environ['LAST_FM_ACTIVE']:
        from utils import last_fm
        song_info = api.get_song_data(song_id)
        last_fm.scrobble(
            song_info['title'],
            song_info['artist'],
            environ['LAST_FM_SESSION_KEY']
        )

    app.logger.debug('URL is %s' % stream_url)

    return redirect(stream_url, code=302)
