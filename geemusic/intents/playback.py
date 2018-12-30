from flask import render_template
from flask_ask import statement, audio
from geemusic import ask, queue, app, api
import json


##
# Callbacks
#


def empty_response():
    return json.dumps({"response": {}, "version": "1.0"}), 200


@ask.on_playback_stopped()
def stopped(offset):
    queue.paused_offset = offset
    app.logger.debug(render_template("stopped", offset=offset))
    return empty_response()


@ask.on_playback_started()
def started(offset):
    app.logger.debug(render_template("started", offset=offset))

    return empty_response()


@ask.on_playback_nearly_finished()
def nearly_finished():
    next_id = queue.up_next()

    if next_id is not None:
        stream_url = api.get_stream_url(next_id)

        return audio().enqueue(stream_url)
    return empty_response()


@ask.on_playback_finished()
def finished():
    queue.next()
    return empty_response()

##
# Intents
#


@ask.intent('GeeMusicRefreshLibrary')
def index():
    api.start_indexing()
    return audio(render_template("indexing"))


@ask.intent('AMAZON.StartOverIntent')
def start_over():
    next_id = queue.current()

    if next_id is None:
        return audio(render_template("start_over"))
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio(render_template("resume")).resume()


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio(render_template("pause")).stop()


@ask.intent('AMAZON.StopIntent')
def stop():
    queue.reset()
    return audio(render_template("stop")).stop()


@ask.intent('AMAZON.NextIntent')
def next_song():
    next_id = queue.next()

    if next_id is None:
        return audio(render_template("next_song"))
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.PreviousIntent')
def prev_song():
    prev_id = queue.prev()

    if prev_id is None:
        return audio(render_template("prev_song"))
    else:
        stream_url = api.get_stream_url(prev_id)

        return audio().play(stream_url)


@ask.intent("AMAZON.ShuffleOnIntent")
def shuffle_on():
    if len(queue.song_ids) == 0:
        return statement(render_template("shuffle_on"))

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent("AMAZON.ShuffleOffIntent")
def shuffle_off():
    if len(queue.song_ids) == 0:
        return statement(render_template("shuffle_off"))

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOnIntent')
def loop_on():
    if len(queue.song_ids) == 0:
        return statement(render_template("loop_text"))

    first_song_id = queue.loop_mode(True)

    stream_url = api.get_stream_url(first_song_id)
    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOffIntent')
def loop_off():
    if len(queue.song_ids) == 0:
        return statement(render_template("loop_text"))

    first_song_id = queue.loop_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('GeeMusicCurrentlyPlayingIntent')
def currently_playing():
    if api.is_indexing():
        return statement(render_template("indexing"))

    track = queue.current_track()

    if track is None:
        return audio(render_template("currently_playing_none"))

    if 'albumArtRef' in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    return statement(render_template("success_title")
                     + render_template("success_text",
                                       song=track['title'],
                                       artist=track['artist']))\
        .standard_card(title=render_template("success_title"),
                       text=render_template("success_text",
                                            song=track['title'],
                                            artist=track['artist']),
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent('GeeMusicListAllPlaylists')
def list_all_playlists():
    if api.is_indexing():
        return statement(render_template("indexing"))

    all_playlists = api.get_all_user_playlist_contents()
    playlist_names = []
    total_playlists = 0
    for i, match in enumerate(all_playlists):

        playlist_names.append(match['name'])
        total_playlists = i + 1

    # Adds "and" before the last playlist to sound more natural when speaking
    if len(playlist_names) >= 3:
        and_placement = len(playlist_names) - 1
        playlist_names.insert(and_placement, render_template("playlist_separator"))

    app.logger.debug(playlist_names)
    playlist_names = ', '.join(playlist_names)

    speech_text = render_template("list_all_playlists_text",
                                  playlist_count=total_playlists,
                                  playlist_list=playlist_names)
    return statement(speech_text)


@ask.intent("GeeMusicThumbsUpIntent")
def thumbs_up():
    if len(queue.song_ids) == 0:
        return statement(render_template("thumbs_no_song"))

    if api.is_indexing():
        return statement(render_template("indexing"))

    api.rate_song(queue.current_track(), '5')

    return statement(render_template("thumbs_up_text"))


@ask.intent("GeeMusicThumbsDownIntent")
def thumbs_down():
    if len(queue.song_ids) == 0:
        return statement(render_template("thumbs_no_song"))

    if api.is_indexing():
        return statement(render_template("indexing"))

    api.rate_song(queue.current_track(), '1')

    return statement(render_template("thumbs_down_text"))


@ask.intent("GeeMusicRestartTracksIntent")
def restart_tracks():
    if len(queue.song_ids) == 0:
        return statement(render_template("restart_tracks_none"))

    queue.current_index = 0
    stream_url = api.get_stream_url(queue.current())
    return audio(render_template("restart_tracks_text")).play(stream_url)


@ask.intent("GeeMusicSkipTo")
# https://github.com/stevenleeg/geemusic/issues/28
def skip_to(song_name, artist_name):
    if song_name is None:
        return statement(render_template("skip_to_no_song"))

    if artist_name is None:
        artist_name = ""
    best_match = api.closest_match(song_name, queue.tracks, artist_name, 0)

    if best_match is None:
        return statement(render_template("skip_to_no_match"))

    try:
        song, song_id = api.extract_track_info(best_match)
        index = queue.song_ids.index(song_id)
    except:
        return statement(render_template("skip_to_no_song_match"))

    queue.current_index = index
    stream_url = api.get_stream_url(queue.current())

    if "albumArtRef" in queue.current_track():
        thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    else:
        thumbnail = None
    speech_text = render_template("skip_to_speech_text",
                                  song=queue.current_track()['title'],
                                  artist=queue.current_track()['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.session_ended
def session_ended():
    return "", 200
