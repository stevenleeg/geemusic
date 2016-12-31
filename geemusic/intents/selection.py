from flask_ask import statement, audio
from os import environ
from geemusic import ask, app, queue
from geemusic.utils.music import GMusicWrapper
from fuzzywuzzy import fuzz

@ask.intent("GeeMusicPlayArtistIntent")
def play_artist(artist_name):
    api = GMusicWrapper.generate_api()

    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist == False:
        return statement("Sorry, I couldn't find that artist")

    # Setup the queue
    song_ids = map(lambda x: x['storeId'], artist['topTracks'])
    first_song_id = queue.reset(song_ids)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)
    app.logger.debug("Stream URL is %s" % stream_url)

    speech_text = "Playing top tracks from %s" % artist['name']
    return audio(speech_text).play(stream_url)

@ask.intent("GeeMusicPlayAlbumIntent")
def play_album(album_name, artist_name):
    api = GMusicWrapper.generate_api()

    app.logger.debug("Fetching album %s by %s" % (album_name, artist_name))

    # Fetch the album
    album = api.get_album(album_name, artist_name=artist_name)

    if album == False:
        return statement("Sorry, I couldn't find that album")

    # Setup the queue
    song_ids = map(lambda x: x['storeId'], album['tracks'])
    first_song_id = queue.reset(song_ids)

    app.logger.debug('Queue status: %s', queue)
    app.logger.debug('Sending track id: %s', first_song_id)

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing album %s by %s" % (album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)

@ask.intent("GeeMusicPlaySongIntent")
def play_song(song_name, artist_name):
    api = GMusicWrapper.generate_api()
    queue.reset()

    app.logger.debug("Fetching song %s by %s" % (song_name, artist_name))

    # Fetch the song
    song = api.get_song(song_name, artist_name=artist_name)

    if song == False:
        return statement("Sorry, I couldn't find that song")

    # Start streaming the first track
    stream_url = api.get_stream_url(song['storeId'])

    speech_text = "Playing song %s by %s" % (song['title'], song['artist'])
    return audio(speech_text).play(stream_url)

@ask.intent("GeeMusicPlayArtistRadioIntent")
def play_artist_radio(artist_name):
    api = GMusicWrapper.generate_api()

    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist == False:
        return statement("Sorry, I couldn't find that artist")

    station_id = api.get_station("%s Radio" % artist['name'], artist_id=artist['artistId'])
    # TODO: Handle track duplicates
    tracks = api.get_station_tracks(station_id)

    # Sometimes tracks don't have a store id?
    song_ids = map(lambda x: x.get('storeId', None), tracks)
    song_ids = filter(lambda x: x != None, song_ids)

    first_song_id = queue.reset(song_ids)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing %s radio" % artist['name']
    return audio(speech_text).play(stream_url)

@ask.intent("GeeMusicPlayPlaylistIntent")
def play_playlist(playlist_name):
    api = GMusicWrapper.generate_api()

    app.logger.debug("Fetching songs from %s playlist" % (playlist_name))
    # Retreve the content of all playlists in a users library
    allplaylists = api.get_all_user_playlist_contents()
    # Find the closest match for the playlist
    playlist_number = 0
    best_playlist = None
    best_match = 0
    for list in allplaylists:
        # fuzz.ratio returns a number of how similar to strings are (higher is better)
        match = fuzz.ratio(list['name'].lower().replace(" ", ""),
                           playlist_name.lower().replace(" ", ""))
        if match > best_match:
            best_playlist = playlist_number
            best_match = match
        playlist_number += 1
    # may want to raise number (this means there is a 80% similarity)
    if best_match <= 0:
        return statement("Sorry, I couldn't find that playlist in your library.")

    playlistname = allplaylists[best_playlist]['name']
    # appends the song id to song_ids
    # (some songs do not have a store id so it uses the track id instead)
    count = 0
    song_ids = []
    for ids in allplaylists[best_playlist]['tracks']:
        try:
            song_ids.append(allplaylists[best_playlist]['tracks'][count]['track']['storeId'])
        except KeyError:
            song_ids.append(allplaylists[best_playlist]['tracks'][count]['trackId'])
        count += 1

    first_song_id = queue.reset(song_ids)

    # Get a streaming URL for the first song in the playlist
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing songs from %s" % (playlistname)
    return audio(speech_text).play(stream_url) \
        .simple_card(title="Gee Music",
                     content=speech_text)

@ask.intent("GeeMusicPlayIFLRadioIntent")
def play_artist_radio(artist_name):
    api = GMusicWrapper.generate_api()
    # TODO: Handle track duplicates
    tracks = api.get_station_tracks("IFL")

    # Sometimes tracks don't have a store id?
    song_ids = map(lambda x: x.get("storeId", None), tracks)
    song_ids = filter(lambda x: x != None, song_ids)

    first_song_id = queue.reset(song_ids)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing music from your personalized station"
    return audio(speech_text).play(stream_url)
