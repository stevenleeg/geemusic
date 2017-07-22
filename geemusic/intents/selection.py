from flask_ask import statement, audio, question
from geemusic import ask, queue, app, api
from geemusic.utils.music import GMusicWrapper
from random import shuffle


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
    
    #api.get_artist found somthing from store api search 
    if 'topTracks' in artist:
        # Setup the queue
        first_song_id = queue.reset(artist['topTracks'])
        nameKey = 'name'
        trackType = 'top'
        
    else: #api.get_artist searched the uploaded library instead, artist is a list
        shuffle(artist)
        first_song_id = queue.reset(artist)
        #make artist just the first value in the dictionary for the rest of this function
        artist = artist[0]
        nameKey = 'artist'
        trackType = 'random library'

    # Get a streaming URL for the top song
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(artist)
    speech_text = "Playing %s tracks by %s" % (trackType, artist[nameKey])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                        text='',
                        small_image_url=thumbnail,
                        large_image_url=thumbnail)


@ask.intent("GeeMusicPlayAlbumIntent")
def play_album(album_name, artist_name):
    app.logger.debug("Fetching album %s by %s" % (album_name, artist_name))

    # Fetch the album
    album = api.get_album(album_name, artist_name)

    if album is False:
        return statement("Sorry, I couldn't find that album")

    #store dict
    if type(album) is dict:
        # Setup the queue
        first_song_id = queue.reset(album['tracks'])
        albumNameKey = 'name'
    else: #library list
        first_song_id = queue.reset(sorted(album, key=lambda record: record['trackNumber']))
        #make artist just the first value in the dictionary for the rest of this function
        album = album[0]
        albumNameKey = 'album'

    # Start streaming the first track
    stream_url = api.get_stream_url(first_song_id)

    thumbnail = api.get_thumbnail(album)
    speech_text = "Playing album %s by %s" % \
                  (album[albumNameKey], album['albumArtist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


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

    thumbnail = api.get_thumbnail(queue.current_track())
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

    thumbnail = api.get_thumbnail(artist)
    speech_text = "Playing %s radio" % artist['name']
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
        return statement("Sorry, I couldn't find that playlist in your library.")

    # Add songs from the playlist onto our queue
    first_song_id = queue.reset(best_match['tracks'])

    # Get a streaming URL for the first song in the playlist
    stream_url = api.get_stream_url(first_song_id)
    thumbnail = api.get_thumbnail(queue.current_track())
    speech_text = "Playing songs from %s" % (best_match['name'])
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

    speech_text = "Playing music from your personalized station"
    thumbnail = "https://i.imgur.com/NYTSqHZ.png"
    return audio(speech_text).play(stream_url) \
        .standard_card(title="Playing I'm Feeling Lucky Radio",
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


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
    if GMusicWrapper.use_library_first():
        song_id = song['id']
    else:
        song_id = song['storeId']
    queue.enqueue_track(song, song_id)
    stream_url = api.get_stream_url(song)
    card_text = "Queued %s by %s." % (song['title'], song['artist'])
    thumbnail = api.get_thumbnail(song)
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
