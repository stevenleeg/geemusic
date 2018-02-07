from flask_ask import statement, audio
from geemusic import ask, queue, app, api, language
import json


##
# Constants
#

WORDS = {
        "en": {
            "stopped"            : "Stopped at %s",
            "started"            : "Started at %s",
            "start_over"         : "There are no songs on the queue",
            "resume"             : "Resuming",
            "pause"              : "Pausing",
            "stop"               : "Stopping",
            "next_song"          : "There are no more songs on the queue",
            "prev_song"          : "You can't go back any further in the queue.",
            "shuffle_on"         : "There are no songs to shuffle.",
            "shuffle_off"        : "There are no songs to unshuffle.",
            "loop_on"            : "There are no songs in the queue.",
            "loop_off"           : "There are no songs in the queue.",
            "currently_playing"  : {
                "indexing"      : "Please wait for your tracks to finish indexing.",
                "none"          : "Nothing is playing right now",
                "success_title" : "The current track is",
                "success_text"  : "%s by %s" },
            "list_all_playlists" : {
                "indexing"           : "Please wait for your tracks to finish indexing.",
                "playlist_separator" : "and",
                "speech_text"        : "You have %s playlists in your library. They are, %s." },
            "thumbs_up"          : {
                "no_song" : "Please play a song to vote.",
                "indexing": "Please wait for your tracks to finish indexing.",
                "speech_text": "Upvoted" },
            "thumbs_down"        : {
                "no_song"     : "Please play a song to vote.",
                "indexing"    : "Please wait for your tracks to finish indexing.",
                "speech_text" : "Downvoted." },
            "restart_tracks" : {
                "no_song"    : "You must first play tracks to restart them",
                "speech_text": "Restarting tracks." },
            "skip_to" : {
                "no_song"      : "Please say a song name to use this feature.",
                "no_match"     : "Sorry, I couldn't find a close enough match.",
                "no_song_match": "Sorry, I couldn't find that song in the queue.",
                "speech_text"  : "Skipping to %s by %s" },
            },
        "de" : "implement_same_as_above_for_extending_to_german",
        "jp" : "implement_same_as_above_for_extending_to_japanese"
}


##
# Callbacks
#


@ask.on_playback_stopped()
def stopped(offset):
    queue.paused_offset = offset
    app.logger.debug(WORDS[language]["stopped"] % offset)


@ask.on_playback_started()
def started(offset):
    app.logger.debug(WORDS[language]["started"] % offset)


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
        return audio(WORDS[language]["start_over"])
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio(WORDS[language]["resume"]).resume()


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio(WORDS[language]["pause"]).stop()


@ask.intent('AMAZON.StopIntent')
def stop():
    queue.reset()
    return audio('Stopping').stop()


@ask.intent('AMAZON.NextIntent')
def next_song():
    next_id = queue.next()

    if next_id is None:
        return audio(WORDS[language]["next_song"])
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.PreviousIntent')
def prev_song():
    prev_id = queue.prev()

    if prev_id is None:
        return audio(WORDS[language]["prev_song"])
    else:
        stream_url = api.get_stream_url(prev_id)

        return audio().play(stream_url)


@ask.intent("AMAZON.ShuffleOnIntent")
def shuffle_on():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["shuffle_on"])

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent("AMAZON.ShuffleOffIntent")
def shuffle_off():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["shuffle_off"])

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOnIntent')
def loop_on():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["loop_on"])

    first_song_id = queue.loop_mode(True)

    stream_url = api.get_stream_url(first_song_id)
    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOffIntent')
def loop_off():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["loop_off"])

    first_song_id = queue.loop_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('GeeMusicCurrentlyPlayingIntent')
def currently_playing():
    if api.is_indexing():
        return statement(WORDS[language]["currently_playing"]["indexing"])

    track = queue.current_track()

    if track is None:
        return audio(WORDS[language]["currently_playing"]["none"])

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    return statement(WORDS[language]["currently_playing"]["success_title"] \
                           + WORDS[language]["currently_playing"]["success_text"] \
                           % (track['title'], track['artist'])) \
                           .standard_card(title=WORDS[language]["currently_playing"]["success_title"],
                     text=WORDS[language]["currently_playing"]["success_text"] % (track['title'], track['artist']),
                     small_image_url=thumbnail,
                     large_image_url=thumbnail)


@ask.intent('GeeMusicListAllPlaylists')
def list_all_playlists():
    if api.is_indexing():
        return statement(WORDS[language]["list_all_playlists"]["indexing"])

    all_playlists = api.get_all_user_playlist_contents()
    playlist_names = []
    for i, match in enumerate(all_playlists):

        playlist_names.append(match['name'])
        total_playlists = i + 1

    # Adds "and" before the last playlist to sound more natural when speaking
    if len(playlist_names) >= 3:
        and_placement = len(playlist_names) - 1
        playlist_names.insert(and_placement, WORDS[language]["list_all_playlists"]["playlist_separator"])

    app.logger.debug(playlist_names)
    playlist_names = ', '.join(playlist_names)

    speech_text = WORDS[language]["list_all_playlists"]["speech_text"] % (total_playlists, playlist_names)
    return statement(speech_text)


@ask.intent("GeeMusicThumbsUpIntent")
def thumbs_up():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["thumbs_up"]["no_song"])

    if api.is_indexing():
        return statement(WORDS[language]["thumbs_up"]["indexing"])

    api.rate_song(queue.current_track(), '5')

    return statement(WORDS[language]["thumbs_up"]["speech_text"])


@ask.intent("GeeMusicThumbsDownIntent")
def thumbs_down():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["thumbs_down"]["no_song"])

    if api.is_indexing():
        return statement(WORDS[language]["thumbs_down"]["indexing"])

    api.rate_song(queue.current_track(), '1')

    return statement(WORDS[language]["thumbs_down"]["speech_text"])


@ask.intent("GeeMusicRestartTracksIntent")
def restart_tracks():
    if len(queue.song_ids) == 0:
        return statement(WORDS[language]["restart_tracks"]["no_song"])

    queue.current_index = 0
    stream_url = api.get_stream_url(queue.current())
    return audio(WORDS[language]["restart_tracks"]["speech_text"]).play(stream_url)


@ask.intent("GeeMusicSkipTo")
# https://github.com/stevenleeg/geemusic/issues/28
def skip_to(song_name, artist_name):
    if song_name is None:
        return statement(WORDS[language]["skip_to"]["no_song"])

    if artist_name is None:
        artist_name = ""
    best_match = api.closest_match(song_name, queue.tracks, artist_name, 0)

    if best_match is None:
        return statement(WORDS[language]["skip_to"]["no_match"])

    try:
        song, song_id = api.extract_track_info(best_match)
        index = queue.song_ids.index(song_id)
    except:
        return statement(WORDS[language]["skip_to"]["no_song_match"])

    queue.current_index = index
    stream_url = api.get_stream_url(queue.current())

    thumbnail = api.get_thumbnail(queue.current_track()['albumArtRef'][0]['url'])
    speech_text = WORDS[language]["skip_to"]["speech_text"] % (queue.current_track()['title'], queue.current_track()['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.session_ended
def session_ended():
    return "", 200
