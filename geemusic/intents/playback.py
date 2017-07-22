from flask_ask import statement, audio
from geemusic import ask, queue, app, api

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
        return audio("There are no songs on the queue")
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
        return audio("There are no more songs on the queue")
    else:
        stream_url = api.get_stream_url(next_id)

        return audio().play(stream_url)


@ask.intent('AMAZON.PreviousIntent')
def prev_song():
    prev_id = queue.prev()

    if prev_id is None:
        return audio("You can't go back any farther in the queue")
    else:
        stream_url = api.get_stream_url(prev_id)

        return audio().play(stream_url)


@ask.intent("AMAZON.ShuffleOnIntent")
def shuffle_on():
    if len(queue.song_ids) == 0:
        return statement("There are no songs to shuffle.")

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(True)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent("AMAZON.ShuffleOffIntent")
def shuffle_off():
    if len(queue.song_ids) == 0:
        return statement("There are no songs to unshuffle.")

    # Start streaming the first track in the new shuffled list
    first_song_id = queue.shuffle_mode(False)
    stream_url = api.get_stream_url(first_song_id)

    return audio().enqueue(stream_url)


@ask.intent('AMAZON.LoopOnIntent')
def loop_on():
    if len(queue.song_ids) == 0:
        return statement("There are no songs in the queue.")

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
        return statement("Please wait for your tracks to finish indexing")

    track = queue.current_track()

    if track is None:
        return audio("Nothing is playing right now")

    thumbnail = api.get_thumbnail(queue.current_track())
    return statement("The current track is %s by %s" % (track['title'],
                                                        track['artist'])) \
        .standard_card(title="The current track is",
                       text='%s by %s' % (track['title'], track['artist']),
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.intent("GeeMusicThumbsUpIntent")
def thumbs_up():
    if len(queue.song_ids) == 0:
        return statement("Please play a song to vote")

    if api.is_indexing():
        return statement("Please wait for your tracks to finish indexing")

    api.rate_song(queue.current_track(), '5')

    return statement("Upvoted")


@ask.intent("GeeMusicThumbsDownIntent")
def thumbs_down():
    if len(queue.song_ids) == 0:
        return statement("Please play a song to vote")

    if api.is_indexing():
        return statement("Please wait for your tracks to finish indexing")

    api.rate_song(queue.current_track(), '1')

    return statement("Downvoted")


@ask.intent("GeeMusicRestartTracksIntent")
def restart_tracks():
    if len(queue.song_ids) == 0:
        return statement("You must first play tracks to restart them")

    queue.current_index = 0
    stream_url = api.get_stream_url(queue.current())
    return audio("Restarting tracks").play(stream_url)


@ask.intent("GeeMusicSkipTo")
# https://github.com/stevenleeg/geemusic/issues/28
def skip_to(song_name, artist_name):
    if song_name is None:
        return statement("Please say a song name to use this feature")

    if artist_name is None:
        artist_name = ""
    best_match = api.closest_match(song_name, queue.tracks, artist_name, 30)

    if best_match is None:
        return statement("Sorry, I couldn't find a close enough match.")

    try:
        song, song_id = api.extract_track_info(best_match)
        index = queue.song_ids.index(song_id)
    except:
        return statement("Sorry, I couldn't find that song in the queue")

    queue.current_index = index
    stream_url = api.get_stream_url(queue.current())

    thumbnail = api.get_thumbnail(queue.current_track())
    speech_text = "Skipping to %s by %s" % (queue.current_track()['title'], queue.current_track()['artist'])
    return audio(speech_text).play(stream_url) \
        .standard_card(title=speech_text,
                       text='',
                       small_image_url=thumbnail,
                       large_image_url=thumbnail)


@ask.session_ended
def session_ended():
    return "", 200
