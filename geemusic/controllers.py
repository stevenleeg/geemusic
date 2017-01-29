from flask import redirect
from geemusic import app, api


@app.route("/geemusic/stream/<song_id>")
def redirect_to_stream(song_id):
    stream_url = api.get_google_stream_url(song_id)

    app.logger.debug('URL is %s' % stream_url)
    return redirect(stream_url, code=302)
