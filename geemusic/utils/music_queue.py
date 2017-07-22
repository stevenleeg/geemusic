from builtins import object
import random


class MusicQueue(object):
    def __init__(self, api, tracks=[]):
        self.reset(tracks)
        self.current_index = 0
        self.api = api

    def next(self):
        self.api.increment_song_playcount(self.current())
        if len(self.song_ids) == 0 or \
                self.current_index + 1 >= len(self.song_ids):
            return None
        if len(self.song_ids_backup['loop']) > 0:
            return self.song_ids[self.current_index]

        self.current_index += 1
        return self.song_ids[self.current_index]

    def up_next(self):
        if len(self.song_ids) == 0 or \
                self.current_index + 1 >= len(self.song_ids):
            return None
        if len(self.song_ids_backup['loop']) > 0:
            return self.song_ids[self.current_index]

        return self.song_ids[self.current_index + 1]

    def prev(self):
        if len(self.song_ids) == 0 or self.current_index - 1 < 0:
            return None
        if len(self.song_ids_backup['loop']) > 0:
            return self.song_ids[self.current_index]

        self.current_index -= 1
        return self.song_ids[self.current_index]

    def current(self):
        if len(self.song_ids) == 0:
            return None

        return self.song_ids[self.current_index]

    def current_track(self):
        if len(self.song_ids) == 0:
            return None
        return self.tracks[self.current()]

    def reset(self, tracks=[]):
        self.tracks = {}
        self.song_ids_backup = dict()
        self.song_ids_backup['loop'] = []
        self.song_ids = []

        for track in tracks:
            track, song_id = self.api.extract_track_info(track)
            if track is None:
                continue

            self.song_ids.append(song_id)
            self.tracks[song_id] = track

        self.current_index = 0

        if len(self.song_ids) == 0:
            return None
        else:
            return self.song_ids[self.current_index]

    def enqueue_track(self, song, song_id):
        self.song_ids.append(song_id)
        self.tracks[song_id] = song

        return self.song_ids[self.current_index]

    def shuffle_mode(self, value):
        if value is True:
            self.song_ids_backup['shuffle'] = list(self.song_ids)
            random.shuffle(self.song_ids)
            self.current_index = 0
        elif value is False:
            self.current_index = self.song_ids_backup['shuffle'].index(
                self.song_ids[self.current_index])
            self.song_ids = self.song_ids_backup['shuffle']

        return self.song_ids[self.current_index]

    def loop_mode(self, value):
        if value is True:
            self.song_ids_backup['loop'] = list(self.song_ids)
            self.song_ids = [self.song_ids[self.current_index]]
        elif value is False:
            self.current_index = self.song_ids_backup['loop'].index(
                self.song_ids[self.current_index])
            self.song_ids = self.song_ids_backup['loop']
            self.song_ids_backup['loop'] = []

        return self.song_ids[self.current_index]

    def __str__(self):
        return "<Queue: length=%d position=%d items=%s>" % (
            len(self.song_ids), self.current_index, self.song_ids)
