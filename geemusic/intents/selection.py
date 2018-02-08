from flask_ask import statement, audio, question
from geemusic import ask, queue, app, api, language
from geemusic.utils.music import GMusicWrapper

WORDS = {
    "en" : {
        "login"                      : {
            "text"   : "Welcome to Gee Music. \
                        Try asking me to play a song or start a playlist",
            "prompt" : "For example say, play music by A Tribe Called Quest",
            "title"  : "Welcome to GeeMusic!",
            "content": "Try asking me to play a song" },
        "help"                       : {
            "text"  : ''' Here are some things you can say:
                          Play songs by Radiohead,
                          Play the album Science For Girls,
                          Play the song Fitter Happier,
                          Start a radio station for artist Weezer,
                          Start playlist Dance Party,
                          and play some music,
                          Of course you can also say skip, previous, shuffle, and more
                          of alexa's music commands or, stop, if you're done.
                          ''',
            "prompt": "For example say, play music by A Tribe Called Quest" },
        "play_artist"                : {
            "none"       : "Sorry, I couldn't find that artist.",
            "speech_text": "Playing top tracks by %s" },
        "play_album"                 : {
            "debug"      : "Fetching album %s",
            "no_album"   : "Sorry, I couldn't find that album",
            "speech_text": "Playing album {0} by {1}" },
        "play_promoted_songs"        : {
            "debug"      : "Fetching songs that you have up voted.",
            "no_songs"   : "Sorry, I couldn't find any up voted songs.",
            "speech_text": "Playing your up voted songs." },
        "play_song"                  : {
            "debug"      : "Fetching song {0} by {1}",
            "no_song"    : "Sorry, I couldn't find that song.",
            "speech_text": "Playing {0} by {1}." },
        "play_similar_song_radio"    : {
            "no_song"        : "Please play a song to start radio.",
            "index"          : "Please wait for your tracks to finish indexing.",
            "debug"          : "Fetching songs like {0} by {1} from {2}",
            "no_similar_song": "Sorry, I couldn't find that song.",
            "speech_text"    : "Playing {0} by {1}" },
        "play_song_radio"            : {
            "debug"          : "Fetching song {0} by {1} from {2}.",
            "no_song"        : "Sorry, I couldn't find that song.",
            "speech_text"    : "Playing {0} by {1}." },
        "play_artist_radio"          : {
            "no_artist"      : "Sorry, I couldn't find that artist.",
            "speech_text"    : "Playing %s radio." },
        "play_playlist"              : {
            "no_match"       : "Sorry, I couldn't find that playlist in your library.",
            "speech_text"    : "Playing songs from %s." },
        "play_IFL_radio"             : {
            "speech_text" : "Playing music from your personalized station.",
            "speech_title": "Playing I'm Feeling Lucky Radio." },
        "queue_song"                 : {
            "debug"       : "Queuing song {0} by {1}.",
            "no_song"     : "You must first play a song.",
            "no_match"    : "Sorry, I couldn't find that song.",
            "queued"      : "Queued {0} by {1}." },
        "play_latest_album_by_artist": {
            "no_album"    : "Sorry, I couldn't find any albums.",
            "speech_text" : "Playing album {0} by {1}." },
        "play_album_by_artist"       : {
            "no_album"    : "Sorry, I couldn't find any albums.",
            "speech_text" : "Playing album {0} by {1}." },
        "play_different_album"       : {
            "no_track"    : "Sorry, there's no album playing currently.",
            "no_album"    : "Sorry, I couldn't find any albums.",
            "speech_text" : "Playing album {0} by {1}." },
        "play_library"               : {
            "index"      : "Please wait for your tracks to finish indexing.",
            "speech_text": "Playing music from your library." }
    },
    "jp" : "fill_out_translations_in_same_scaffolding_as_en",
    "de" : "fill_out_translations_in_same_scaffolding_as_en"
}


@ask.launch
def login():
    text = WORDS[language]["login"]["text"]
    prompt = WORDS[language]["login"]["prompt"]
    return question(text).reprompt(prompt) \
        .simple_card(title=WORDS[language]["login"]["title"],
                     content=WORDS[language]["login"]["content"])


@ask.intent("AMAZON.HelpIntent")
def help():
    text = WORDS[language]["login"]["text"]

    prompt = WORDS[language]["login"]["prompt"]
    return question(text).reprompt(prompt)


@ask.intent("GeeMusicPlayArtistIntent")
def play_artist(artist_name):
    # Fetch the artist
    artist = api.get_artist(artist_name)

    if artist is False:
        return statement(WORDS[language]["play_artist"]["none"])

    # Setup the queue
    first_song_id = queue.reset(artist['topTracks'])

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(artist['artistArtRef'])
    speech_text = WORDS[language]["play_artist"]["speech_text"] % artist['name']
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayAlbumIntent")
def play_album(album_name, artist_name):
    app.logger.debug(WORDS[language]["play_album"]["debug"] % album_name)

    # Fetch the album
    album = api.get_album(album_name, artist_name)

    if album is False:
        return statement(WORDS[language]["play_album"]["no_album"])

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(album['albumArtRef'])
    speech_text = WORDS[language]["play_album"]["speech_text"]\
                  .format(album['name'], album['albumArtist'])

    app.logger.debug(speech_text)

    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayThumbsUpIntent")
def play_promoted_songs():
    app.logger.debug(WORDS[language]["play_promoted_songs"]["debug"])
    
    promoted_songs = api.get_promoted_songs()
    if promoted_songs is False:
        return statement(WORDS[language]["play_promoted_songs"]["no_songs"])
    
    first_song_id = queue.reset(promoted_songs)
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["play_promoted_songs"]["speech_text"]
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)    


@ask.intent("GeeMusicPlaySongIntent")
def play_song(song_name, artist_name):
    app.logger.debug(WORDS[language]["play_song"]["debug"].format(song_name, artist_name))

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement(WORDS[language]["play_song"]["no_song"])

    # Start streaming the first track
    first_song_id = queue.reset([song])
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["play_song"]["speech_text"]\
                  .format(song['title'], song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySimilarSongsRadioIntent")
def play_similar_song_radio():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["play_similar_song_radio"]["no_song"])

    if api.is_indexing():
        return statement(WORDS[language]["play_similar_song_radio"]["index"])

    # Fetch the song
    song = queue.current_track()
    artist = api.get_artist(song['artist'])
    album = api.get_album(song['album'])

    app.logger.debug(WORDS[language]["play_similar_song_radio"]["debug"]\
                     .format(song['title'], artist['name'], album['name']))

    if song is False:
        return statement(WORDS[language]["play_similar_song_radio"]["no_similar_song"])

    station_id = api.get_station("%s Radio" %
                                 song['title'], 
                                 track_id=song['storeId'], 
                                 artist_id=artist['artistId'], 
                                 album_id=album['albumId'])

    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["play_similar_song_radio"]["speech_text"]\
                  .format(song['title'], song['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlaySongRadioIntent")
def play_song_radio(song_name, artist_name, album_name):
    app.logger.debug(WORDS[language]["play_song_radio"]["debug"]\
                     .format(song_name, artist_name, album_name))

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
        return statement(WORDS[language]["play_song_radio"]["no_song"])

    station_id = api.get_station("%s Radio" %
                                 song['title'], 
                                 track_id=song['storeId'], 
                                 artist_id=artist['artistId'], 
                                 album_id=album['albumId'])

    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["play_song_radio"]["speech_text"]\
                  .format(song['title'], song['artist'])
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
        return statement(WORDS[language]["play_artist_radio"]["no_artist"])

    station_id = api.get_station("%s Radio" %
                                 artist['name'], artist_id=artist['artistId'])
    # TODO: Handle track duplicates (this may be possible using session ids)
    tracks = api.get_station_tracks(station_id)

    first_song_id = queue.reset(tracks)

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(artist['artistArtRef'])
    speech_text = WORDS[language]["play_artist_radio"]["speech_text"] % artist['name']
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicPlayPlaylistIntent")
def play_playlist(playlist_name):
    # Retreve the content of all playlists in a users library
    all_playlists = api.get_all_user_playlist_contents()

    # Get the closest match
    best_match = api.closest_match(playlist_name, all_playlists)

    if best_match is None:
        return statement(WORDS[language]["play_playlist"]["no_match"])

    # Add songs from the playlist onto our queue
    first_song_id = queue.reset(best_match['tracks'])

    # Get a streaming URL for the first song in the playlist
    stream_url = api.get_stream_url(first_song_id)
    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["play_playlist"]["speech_text"] % (best_match['name'])
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

    speech_text = WORDS[language]["play_IFL_radio"]["speech_text"]
    thumbnail = api.get_thumbnail("https://i.imgur.com/NYTSqHZ.png")
    return audio(speech_text).play(stream_url) \
        .standard_card(title=WORDS[language]["play_IFL_radio"]["speech_title"],
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicQueueSongIntent")
def queue_song(song_name, artist_name):
    app.logger.debug(WORDS[language]["queue_song"]["debug"].format(song_name, artist_name))

    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["queue_song"]["no_song"])

    # Fetch the song
    song = api.get_song(song_name, artist_name)

    if song is False:
        return statement(WORDS[language]["queue_song"]["no_match"])

    # Queue the track in the list of song_ids
    queue.enqueue_track(song)
    stream_url = api.get_stream_url(song)
    card_text = WORDS[language]["queue_song"]["queued"].format(song['title'], song['artist'])
    thumbnail = api.get_thumbnail(song['albumArtRef'][0]['url'])
    return audio().enqueue(stream_url) \
        .standard_card(title=card_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


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
        return statement(WORDS[language]["play_latest_album_by_artist"]["no_album"])

    # Setup the queue
    first_song_id = queue.reset(latest_album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = WORDS[language]["play_latest_album_by_artist"]["speech_text"]\
                  .format(latest_album['name'], latest_album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayAlbumByArtistIntent")
def play_album_by_artist(artist_name):
    api = GMusicWrapper.generate_api()
    album = api.get_album_by_artist(artist_name=artist_name)

    if album is False:
        return statement(WORDS[language]["play_album_by_artist"]["no_album"])

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = WORDS[language]["play_album_by_artist"]["speech_text"]\
                  .format(album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayDifferentAlbumIntent")
def play_different_album():
    api = GMusicWrapper.generate_api()

    current_track = queue.current_track()

    if current_track is None:
        return statement(WORDS[language]["play_different_album"]["no_track"])

    album = api.get_album_by_artist(artist_name=current_track['artist'], album_id=current_track['albumId'])

    if album is False:
        return statement(WORDS[language]["play_different_album"]["no_album"])

    # Setup the queue
    first_song_id = queue.reset(album['tracks'])

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    speech_text = WORDS[language]["play_different_album"]["speech_text"]\
                  .format(album['name'], album['albumArtist'])
    return audio(speech_text).play(stream_url)


@ask.intent("GeeMusicPlayLibraryIntent")
def play_library():
    if api.is_indexing():
        return statement(WORDS[language]["play_library"]["index"])

    tracks = api.library.values()
    first_song_id = queue.reset(tracks)
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    speech_text = WORDS[language]["play_library"]["speech_text"]
    return audio(speech_text).play(stream_url)
