from flask_ask import statement, audio, question
from geemusic import ask, queue, app, api
from geemusic.utils.music import GMusicWrapper


@ask.launch
def login():
    text = 'Welcome to Gee Music. \
            Try asking me to play a song or start a playlist'
    prompt = 'For example say, play music by A Tribe Called Quest'
    return question(text).reprompt(prompt) \
        .simple_card(title='Welcome to GeeMusic!',
                     content='Try asking me to play a song')


@ask.intent("AMAZON.HelpIntent")
def help():
    text = ''' Here are some things you can say:
                Play songs by Radiohead,
                Play the album Science For Girls,
                Play the song Fitter Happier,
                Start a radio station for artist Weezer,
                Start playlist Dance Party,
                and play some music,

                Of course you can also say skip, previous, shuffle, and more
                of alexa's music commands or, stop, if you're done.
                '''

    prompt = 'For example say, play music by A Tribe Called Quest'
    return question(text).reprompt(prompt)


@ask.intent("GeeMusicPlayArtistIntent")
def play_artist(artist_name):
    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist is False:
        return statement("Sorry, I couldn't find that artist")

    # Setup the queue
    first_song_id = queue.reset(artist['topTracks'])

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)
    try:
        thumbnail = api.get_thumbnail(artist['artistArtRef'])
    except:
        thumbnail = ""
    speech_text = "Playing top tracks by %s" % artist['name']
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicPlayAlbumIntent")
def play_album(album_name, artist_name):
    app.logger.debug("Fetching album %s by %s" % (album_name, artist_name))

    # Fetch the album
    album = api.get_album(album_name, artist_name)

    if album is False:
        return statement("Sorry, I couldn't find that album")

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    try:
        thumbnail = api.get_thumbnail(album['albumArtRef'])
    except:
        thumbnail = ""
    speech_text = "Playing album %s by %s" % \
                  (album['name'], album['albumArtist'])
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')

@ask.intent("GeeMusicPlaySongIntent")
def play_song(song_name, artist_name):
    app.logger.debug("Fetching song %s by %s" % (song_name, artist_name))

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement("Sorry, I couldn't find that song")

    # Start streaming the first track
    first_song_id = queue.reset([song])
    stream_url = api.get_stream_url(first_song_id)

    try:
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    except:
        thumbnail = ""
    speech_text = "Playing %s by %s" % (song['title'], song['artist'])
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicPlaySimilarSongsRadioIntent")
def play_similar_song_radio():
    if len(queue.song_ids) == 0:
        return statement("Please play a song to start radio")

    if api.is_indexing():
        return statement("Please wait for your tracks to finish indexing")


    # Fetch the song
    song = queue.current_track()
    artist = api.get_artist(song['artist'])
    album = api.get_album(song['album'])

    app.logger.debug("Fetching songs like %s by %s from %s" % (song['title'], artist['name'], album['name']))

    if song is False:
        return statement("Sorry, I couldn't find that song")

    station_id = api.get_station("%s Radio" %
                                 song['title'], track_id=song['storeId'], artist_id=artist['artistId'], album_id=album['albumId'])
    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = "Playing %s by %s" % (song['title'], song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySongRadioIntent")
def play_song_radio(song_name, artist_name, album_name):
    app.logger.debug("Fetching song %s by %s from %s" % (song_name, artist_name, album_name))

    # Fetch the song

    song = api.get_song(song_name, artist_name, album_name)
    if artist_name is not None:
        artist = api.get_artist(artist_name)
    else:
        artist = api.get_artist(song['artist'])

    if album_name is not None:
        album = api.get_album(album_name)
    else:
        album = api.get_album(song['album'])


    if song is False:
        return statement("Sorry, I couldn't find that song")

    station_id = api.get_station("%s Radio" %
                                 song['title'], track_id=song['storeId'], artist_id=artist['artistId'], album_id=album['albumId'])
    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = "Playing %s by %s" % (song['title'], song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayArtistRadioIntent")
def play_artist_radio(artist_name):
    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist is False:
        return statement("Sorry, I couldn't find that artist")

    station_id = api.get_station("%s Radio" %
                                 artist['name'], artist_id=artist['artistId'])
    # TODO: Handle track duplicates (this may be possible using session ids)
    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    try:
        thumbnail = api.get_thumbnail(artist['artistArtRef'])
    except:
        thumbnail = ""
    speech_text = "Playing %s radio" % artist['name']
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicPlayPlaylistIntent")
def play_playlist(playlist_name):
    # Retreve the content of all playlists in a users library
    all_playlists = api.get_all_user_playlist_contents()

    # Get the closest match
    best_match = api.closest_match(playlist_name, all_playlists)

    if best_match is None:
        return statement("Sorry, I couldn't find that playlist in your library.")

    # Add songs from the playlist onto our queue
    first_song_id = queue.reset(best_match['tracks'])

    # Get a streaming URL for the first song in the playlist
    stream_url = api.get_stream_url(first_song_id)
    try:
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    except:
        thumbnail = ""
    speech_text = "Playing songs from %s" % (best_match['name'])
    if (thumbnail != ""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicPlayIFLRadioIntent")
def play_IFL_radio(artist_name):
    # TODO: Handle track duplicates?
    tracks = api.get_station_tracks("IFL")

    # Get a streaming URL for the first song
    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing music from your personalized station"
    try:
        thumbnail = api.get_thumbnail("https://i.imgur.com/NYTSqHZ.png")
    except:
        thumbnail = ""
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicQueueSongIntent")
def queue_song(song_name, artist_name):
    app.logger.debug("Queuing song %s by %s" % (song_name, artist_name))

    if len(queue.song_ids) == 0:
        return statement("You must first play a song")

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement("Sorry, I couldn't find that song")

    # Queue the track in the list of song_ids
    queue.enqueue_track(song)
    stream_url = api.get_stream_url(song)
    card_text = "Queued %s by %s." % (song['title'], song['artist'])
    try:
        thumbnail = api.get_thumbnail(song['albumArtRef'][0]['url'])
    except:
        thumbnail = ""
    if (thumbnail==""):
        return audio(speech_text).play(stream_url) \
                                 .standard_card(title=speech_text,
                                                text='',
                                                small_image_url=thumbnail,
                                                large_image_url=thumbnail)
    else:
        return audio(speech_text).play(stream_url) \
         .simple_card(title=speech_text, content='')


@ask.intent("GeeMusicListAllAlbumsIntent")
def list_album_by_artists(artist_name):
    api = GMusicWrapper.generate_api()
    artist_album_list = api.get_artist_album_list(artist_name=artist_name)
    return statement(artist_album_list)


@ask.intent("GeeMusicListLatestAlbumIntent")
def list_latest_album_by_artist(artist_name):
    api = GMusicWrapper.generate_api()
    latest_album = api.get_latest_artist_albums(artist_name=artist_name)
    return statement(latest_album)


@ask.intent("GeeMusicPlayLatestAlbumIntent")
def play_latest_album_by_artist(artist_name):
    api = GMusicWrapper.generate_api()
    latest_album = api.get_latest_album(artist_name)

    if latest_album is False:
        return statement("Sorry, I couldn't find any albums")

    # Setup the queue
    first_song_id = queue.reset(latest_album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing album %s by %s" % (latest_album['name'], latest_album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayAlbumByArtistIntent")
def play_album_by_artist(artist_name):
    api = GMusicWrapper.generate_api()
    album = api.get_album_by_artist(artist_name=artist_name)

    if album is False:
        return statement("Sorry, I couldn't find any albums.")

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing album %s by %s" % (album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayDifferentAlbumIntent")
def play_different_album():
    api = GMusicWrapper.generate_api()

    current_track = queue.current_track()

    if current_track is None:
        return statement("Sorry, there's no album playing currently")

    album = api.get_album_by_artist(artist_name=current_track['artist'], album_id=current_track['albumId'])

    if album is False:
        return statement("Sorry, I couldn't find any albums.")

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing album %s by %s" % (album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayLibraryIntent")
def play_library():
    if api.is_indexing():
        return statement("Please wait for your tracks to finish indexing")

    tracks = api.library.values()
    first_song_id = queue.reset(tracks)
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    speech_text = "Playing music from your library"
    return audio(speech_text).play(stream_url)
