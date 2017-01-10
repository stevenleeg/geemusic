import random


class MusicQueue:
    def __init__(self, tracks=[]):
        self.reset(tracks)
        self.current_index = 0

    def next(self):
        if len(self.song_ids) == 0:
            return None
        elif self.current_index + 1 >= len(self.song_ids):
            self.current_index = 0
        else:
            self.current_index += 1

        return self.song_ids[self.current_index]

    def up_next(self):
        if len(self.song_ids) == 0:
            return None
        elif self.current_index + 1 >= len(self.song_ids):
            next_track_index = 0
        else:
            next_track_index = self.current_index + 1

        return self.song_ids[next_track_index]

    def prev(self):
        if len(self.song_ids) == 0:
            return None
        elif self.current_index - 1 < 0:
            self.current_index = len(self.song_ids) - 1
            print len(self.song_ids)
            print self.current_index
        else:
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
            # when coming from a playlist, track info is nested
            # under the "track" key
            if 'track' in track:
                track = track['track']

            if 'storeId' in track:
                song_id = track['storeId']
            elif 'trackId' in track:
                song_id = track['trackId']
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
            self.unshuffled_song_ids = list(self.song_ids)
            random.shuffle(self.song_ids)
            self.current_index = -1
        elif value is False:
            self.current_index = self.unshuffled_song_ids.index(
                self.song_ids[self.current_index])
            self.song_ids = self.unshuffled_song_ids

        return self.song_ids[self.current_index + 1]

    def loop_mode(self, value):
        if value is True:
            self.ordered_song_ids = list(self.song_ids)
            self.song_ids = [self.song_ids[self.current_index]]
            self.current_index = -1
        elif value is False:
            self.current_index = self.ordered_song_ids.index(
                self.song_ids[self.current_index])
            self.song_ids = self.ordered_song_ids

        return self.song_ids[self.current_index + 1]

    def __str__(self):
        return "<Queue: length=%d position=%d items=%s>" % (len(self.song_ids), self.current_index, self.song_ids)
