from flask_ask import statement, audio
from geemusic import ask, queue, app, api
import json

##
# Callbacks
#


@ask.on_playback_stopped()
def stopped(offset):
    queue.paused_offset = offset
    app.logger.debug("Stopped at %s" % offset)


@ask.on_playback_started()
def started(offset):
    app.logger.debug("Started at %s" % offset)


@ask.on_playback_nearly_finished()
def nearly_finished():
    next_id = queue.up_next()

    if next_id is not None:
        stream_url = api.get_stream_url(next_id)

        return audio().enqueue(stream_url)


@ask.on_playback_finished()
def finished():
    queue.next()

##
# Intents
#


@ask.intent('AMAZON.StartOverIntent')
def start_over():
    next_id = queue.current()

    if next_id is None:
        return audio("Es sind keine Songs eingereiht")
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming').resume()


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Pausing').stop()


@ask.intent('AMAZON.StopIntent')
def stop():
    queue.reset()
    return audio('Stopping').stop()


@ask.intent('AMAZON.NextIntent')
def next_song():
    next_id = queue.next()

    if next_id is None:
        return audio("Es sind keine weiteren Songs mehr in der Warteschlange.")
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.PreviousIntent')
def prev_song():
    prev_id = queue.prev()

    if prev_id is None:
        return audio("Du bist am Anfang der Warteschlange.")
    else:
        stream_url = api.get_stream_url(prev_id)

        return audio().play(stream_url)


@ask.intent("AMAZON.ShuffleOnIntent")
def shuffle_on():
    if len(queue.song_ids) == 0:
        return statement("Es sind keine Lieder zur Zufallswiedergabe ausgewählt.")

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent("AMAZON.ShuffleOffIntent")
def shuffle_off():
    if len(queue.song_ids) == 0:
        return statement("Es sind keine Lieder zum Sortieren vorhanden.")

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOnIntent')
def loop_on():
    if len(queue.song_ids) == 0:
        return statement("Es sind keine Lieder in der Warteschlange.")

    first_song_id = queue.loop_mode(True)

    stream_url = api.get_stream_url(first_song_id)
    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOffIntent')
def loop_off():
    if len(queue.song_ids) == 0:
        return statement("There are no songs in the queue.")

    first_song_id = queue.loop_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('GeeMusicCurrentlyPlayingIntent')
def currently_playing():
    if api.is_indexing():
        return statement("Bitte warte, bis deine Lieder zu Ende eingelesen wurden.")

    track = queue.current_track()

    if track is None:
        return audio("Gerade spielt nichts.")

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    return statement("Das aktuelle Lied ist %s von %s" % (track['title'],
                                                        track['artist'])) \
        .standard_card(title="Das aktuelle Lied ist",
                       text='%s von %s' % (track['title'], track['artist']),
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent('GeeMusicListAllPlaylists')
def list_all_playlists():
    if api.is_indexing():
        return statement("Bitte warte, bis deine Lieder zu Ende eingelesen wurden.")

    all_playlists = api.get_all_user_playlist_contents()
    playlist_names = []
    for i, match in enumerate(all_playlists):

        playlist_names.append(match['name'])
        total_playlists = i + 1

    # Adds "and" before the last playlist to sound more natural when speaking
    if len(playlist_names) >= 3:
        and_placement = len(playlist_names) - 1
        playlist_names.insert(and_placement, 'and')

    app.logger.debug(playlist_names)
    playlist_names = ', '.join(playlist_names)

    speech_text = "Du hast %s Playlists in deiner Sammlung. Hier sind deine Playlists: %s." % (total_playlists, playlist_names)
    return statement(speech_text)


@ask.intent("GeeMusicThumbsUpIntent")
def thumbs_up():
    if len(queue.song_ids) == 0:
        return statement("Bitte spiele einen Song ab, um ihn bewerten zu können.")

    if api.is_indexing():
        return statement("Bitte warte, bis deine Lieder zu Ende eingelesen wurden.")

    api.rate_song(queue.current_track(), '5')

    return statement("Dir gefällt das.")


@ask.intent("GeeMusicThumbsDownIntent")
def thumbs_down():
    if len(queue.song_ids) == 0:
        return statement("Bitte spiele einen Song ab, um ihn bewerten zu können.")

    if api.is_indexing():
        return statement("Bitte warte, bis deine Lieder zu Ende eingelesen wurden.")

    api.rate_song(queue.current_track(), '1')

    return statement("Dir gefällt das nicht.")


@ask.intent("GeeMusicRestartTracksIntent")
def restart_tracks():
    if len(queue.song_ids) == 0:
        return statement("Du musst Lieder hören, um sie neustarten zu können.)

    queue.current_index = 0
    stream_url = api.get_stream_url(queue.current())
    return audio("Starte Lied neu").play(stream_url)


@ask.intent("GeeMusicSkipTo")
# https://github.com/stevenleeg/geemusic/issues/28
def skip_to(song_name, artist_name):
    if song_name is None:
        return statement("Bitte sag einen Liednamen um dahin zu wechseln.")

    if artist_name is None:
        artist_name = ""
    best_match = api.closest_match(song_name, queue.tracks, artist_name, 0)

    if best_match is None:
        return statement("Entschuldigung, ich habe das nicht gefunden.")

    try:
        song, song_id = api.extract_track_info(best_match)
        index = queue.song_ids.index(song_id)
    except:
        return statement("Entschuldigung, ich habe dieses Lied in deiner Warteschlange nicht gefunden.")

    queue.current_index = index
    stream_url = api.get_stream_url(queue.current())

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = "Springe zu %s von %s" % (queue.current_track()['title'], queue.current_track()['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.session_ended
def session_ended():
    return "", 200
