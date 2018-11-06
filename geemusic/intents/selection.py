from flask import render_template
from flask_ask import statement, audio, question
from geemusic import ask, queue, app, api
from geemusic.utils.music import GMusicWrapper


@ask.launch
def login():
    text = render_template("login_text")
    prompt = render_template("login_text")
    return question(text).reprompt(prompt) \
        .simple_card(title=render_template("login_title"),
                     content=render_template("login_content"))


@ask.intent("AMAZON.HelpIntent")
def help():
    text = render_template("help_text")
    prompt = render_template("help_prompt")
    return question(text).reprompt(prompt)


@ask.intent("GeeMusicPlayArtistIntent")
def play_artist(artist_name):
    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist is False:
        return statement(render_template("play_artist_none", artist=artist_name))

    # Setup the queue
    first_song_id = queue.reset(artist['topTracks'])

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(artist['artistArtRef'])
    if api.use_store:
        speech_text = render_template("play_artist_text", artist=artist['name'])
    else:
        speech_text = render_template("play_artist_text_library", artist=artist['name'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayAlbumIntent")
def play_album(album_name, artist_name):
    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    app.logger.debug("Fetching album %s" % album_name)

    # Fetch the album
    album = api.get_album(album_name, artist_name)

    if album is False:
        return statement(render_template("no_album"))

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in album:
        thumbnail = api.get_thumbnail(album['albumArtRef'])
    else:
        thumbnail = None
    speech_text = render_template("play_album_text",
                                  album=album['name'],
                                  artist=album['albumArtist'])

    app.logger.debug(speech_text)

    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayThumbsUpIntent")
def play_promoted_songs():
    app.logger.debug("Fetching songs that you have up voted.")

    promoted_songs = api.get_promoted_songs()
    if promoted_songs is False:
        return statement(render_template("play_promoted_songs_no_songs"))

    first_song_id = queue.reset(promoted_songs)
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("play_promoted_songs_text")
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySongIntent")
def play_song(song_name, artist_name):
    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    app.logger.debug("Fetching song %s by %s" % (song_name, artist_name))

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement(render_template("no_song"))

    # Start streaming the first track
    first_song_id = queue.reset([song])
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("play_song_text",
                                  song=song['title'],
                                  artist=song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySimilarSongsRadioIntent")
def play_similar_song_radio():
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    if len(queue.song_ids) == 0:
        return statement(render_template("play_similar_song_radio_no_song"))

    if api.is_indexing():
        return statement(render_template("indexing"))

    # Fetch the song
    song = queue.current_track()
    artist = api.get_artist(song['artist'])
    album = api.get_album(song['album'])

    app.logger.debug("Fetching songs like %s by %s from %s"
                     % (song['title'], artist['name'], album['name']))

    if song is False:
        return statement(render_template("no_song"))

    station_id = api.get_station("%s Radio" % song['title'],
                                 track_id=song['storeId'],
                                 artist_id=artist['artistId'],
                                 album_id=album['albumId'])

    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("play_song_radio_text",
                                  song=song['title'],
                                  artist=song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySongRadioIntent")
def play_song_radio(song_name, artist_name, album_name):
    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    app.logger.debug("Fetching song %s by %s from %s."
                     % (song_name, artist_name, album_name))

    # Fetch the song

    song = api.get_song(song_name, artist_name, album_name)

    if song is False:
        return statement(render_template("no_song"))

    if artist_name is not None:
        artist = api.get_artist(artist_name)
    else:
        artist = api.get_artist(song['artist'])

    if album_name is not None:
        album = api.get_album(album_name)
    else:
        album = api.get_album(song['album'])

    station_id = api.get_station("%s Radio" %
                                 song['title'],
                                 track_id=song['storeId'],
                                 artist_id=artist['artistId'],
                                 album_id=album['albumId'])

    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("play_song_text",
                                  song=song['title'],
                                  artist=song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayArtistRadioIntent")
def play_artist_radio(artist_name):
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist is False:
        return statement(render_template("no_artist"))

    station_id = api.get_station("%s Radio" % artist['name'],
                                 artist_id=artist['artistId'])
    # TODO: Handle track duplicates (this may be possible using session ids)
    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    if "albumArtRef" in album:
        thumbnail = api.get_thumbnail(album['albumArtRef'])
    else:
        thumbnail = None
    speech_text = render_template("play_artist_radio_text",
                                  artist=artist['name'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayPlaylistIntent")
def play_playlist(playlist_name):
    if not api.use_store and api.is_indexing():
        return statement(render_template("indexing"))

    # Retreve the content of all playlists in a users library
    all_playlists = api.get_all_user_playlist_contents()

    # Get the closest match
    best_match = api.closest_match(playlist_name, all_playlists)

    if best_match is None:
        return statement(render_template("play_playlist_no_match"))

    # Add songs from the playlist onto our queue
    first_song_id = queue.reset(best_match['tracks'])

    # Get a streaming URL for the first song in the playlist
    stream_url = api.get_stream_url(first_song_id)
    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("play_playlist_text", playlist=best_match['name'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayIFLRadioIntent")
def play_IFL_radio(artist_name):
    # TODO: Handle track duplicates?
    tracks = api.get_station_tracks("IFL")

    # Get a streaming URL for the first song
    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    speech_text = render_template("play_IFL_radio_text")
    thumbnail = api.get_thumbnail("https://i.imgur.com/NYTSqHZ.png")
    return audio(speech_text).play(stream_url) \
        .standard_card(title=render_template("play_IFL_radio_title"),
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicQueueSongIntent")
def queue_song(song_name, artist_name):
    app.logger.debug("Queuing song %s by %s" % (song_name, artist_name))

    if len(queue.song_ids) == 0:
        return statement(render_template("queue_song_no_song"))

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement(render_template("no_song"))

    # Queue the track in the list of song_ids
    queue.enqueue_track(song)
    stream_url = api.get_stream_url(song)
    card_text = render_template("queue_song_queued",
                                song=song['title'],
                                artist=song['artist'])
    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    return audio().enqueue(stream_url) \
        .standard_card(title=card_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicListAllAlbumsIntent")
def list_album_by_artists(artist_name):
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    api = GMusicWrapper.generate_api()
    artist_album_list = api.get_artist_album_list(artist_name=artist_name)
    return statement(artist_album_list)


@ask.intent("GeeMusicListLatestAlbumIntent")
def list_latest_album_by_artist(artist_name):
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    api = GMusicWrapper.generate_api()
    latest_album = api.get_latest_artist_albums(artist_name=artist_name)
    return statement(latest_album)


@ask.intent("GeeMusicPlayLatestAlbumIntent")
def play_latest_album_by_artist(artist_name):
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    api = GMusicWrapper.generate_api()
    latest_album = api.get_latest_album(artist_name)

    if latest_album is False:
        return statement(render_template("no_albums"))

    # Setup the queue
    first_song_id = queue.reset(latest_album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = render_template("play_album_text",
                                  album=latest_album['name'],
                                  artist=latest_album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayAlbumByArtistIntent")
def play_album_by_artist(artist_name):
    api = GMusicWrapper.generate_api()
    album = api.get_album_by_artist(artist_name=artist_name)

    if album is False:
        return statement(render_template("no_album"))

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = render_template("play_album_text",
                                  album=album['name'],
                                  artist=album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayDifferentAlbumIntent")
def play_different_album():
    # TODO -- can we do this without a subscription?
    if not api.use_store:
        return statement(render_template("not_supported_without_store"))

    api = GMusicWrapper.generate_api()

    current_track = queue.current_track()

    if current_track is None:
        return statement(render_template("play_different_album_no_track"))

    album = api.get_album_by_artist(artist_name=current_track['artist'], album_id=current_track['albumId'])

    if album is False:
        return statement(render_template("no_album"))

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = render_template("play_album_text",
                                  album=album['name'],
                                  artist=album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayLibraryIntent")
def play_library():
    if api.is_indexing():
        return statement(render_template("indexing"))

    tracks = api.library.values()
    first_song_id = queue.reset(tracks)
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    speech_text = render_template("play_library_text")
    return audio(speech_text).play(stream_url)
