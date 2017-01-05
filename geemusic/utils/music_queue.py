import random


class MusicQueue:
    def __init__(self, tracks=[]):
        self.reset(tracks)
        self.current_index = 0

    def next(self):
        if len(self.song_ids) == 0 or self.current_index + 1 >= len(self.song_ids):
            return None

        self.current_index += 1
        return self.song_ids[self.current_index]

    def up_next(self):
        if len(self.song_ids) == 0 or self.current_index + 1 >= len(self.song_ids):
            return None

        return self.song_ids[self.current_index + 1]

    def prev(self):
        if len(self.song_ids) == 0 or self.current_index - 1 < 0:
            return None

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
        self.song_ids = []

        for track in tracks:
            if 'storeId' in track:
                song_id = track['storeId']
            elif 'trackId' in track:
                song_id = track['trackId']
            elif 'track' in track:
                song_id = track['track']['storeId']
            else:
                continue

            self.song_ids.append(song_id)
            self.tracks[song_id] = track

        self.current_index = 0

        if len(self.song_ids) == 0:
            return None
        else:
            return self.song_ids[self.current_index]

    def shuffle_mode(self, value):
        if value is True:
            self.cached_song_ids = list(self.song_ids)
            random.shuffle(self.song_ids)
        elif value is False:
            self.song_ids = self.cached_song_ids

        self.current_index = 0
        return self.song_ids[self.current_index]

    def __str__(self):
        return "<Queue: length=%d position=%d items=%s>" % (len(self.song_ids), self.current_index, self.song_ids)
