from flask_ask import statement, audio
from os import environ
from geemusic import ask, app
from geemusic.utils.music import GMusicWrapper

@ask.intent("GeeMusicPlayArtistIntent")
def hello(artist_name):
    api = GMusicWrapper(environ['GOOGLE_EMAIL'], environ['GOOGLE_PASSWORD'])

    # Fetch the artist
    artist = api.get_artist(artist_name)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(artist['topTracks'][0]['storeId'])

    speech_text = "Playing top tracks from %s" % artist['name']
    return audio(speech_text).play(stream_url)

@ask.intent("GeeMusicPlayAlbumIntent")
def hello(album_name, artist_name):
    api = GMusicWrapper(environ['GOOGLE_EMAIL'], environ['GOOGLE_PASSWORD'])

    app.logger.debug("Fetching album %s by %s" % (album_name, artist_name))

    # Fetch the album
    album = api.get_album(album_name, artist_name=artist_name)
    stream_url = api.get_stream_url(album['tracks'][0]['storeId'])

    speech_text = "Playing album %s by %s" % (album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)

