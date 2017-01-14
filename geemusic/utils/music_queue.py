from geemusic.utils.music import GMusicWrapper
import random
import threading

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
        self.song_ids_to_map = []

        for track in tracks:
            # when coming from a playlist, track info is nested
            # under the "track" key
            if 'track' in track:
                track = track['track']

            if 'storeId' in track:
                song_id = track['storeId']
                self.tracks[song_id] = track
            elif 'trackId' in track:
                song_id = track['trackId']
                self.song_ids_to_map.append(song_id)
            else:
                continue

            self.song_ids.append(song_id)

        # GPM doesn't give track metadata for tracks you've uploaded
        # when you request a playlist. So we have to look it up.
        if len(self.song_ids_to_map) is not 0:
            self.map_user_uploaded_songs = threading.Thread(
                target=self.map_track_metadata())
            self.map_user_uploaded_songs.start()

        self.current_index = 0

        if len(self.song_ids) == 0:
            return None
        else:
            return self.song_ids[self.current_index]

    def map_track_metadata(self):
        api = GMusicWrapper.generate_api()
        tracks_in_library = api.get_all_songs()
        for song_id in self.song_ids_to_map:
            for track in tracks_in_library:
                if song_id == track['id']:
                    self.tracks[song_id] = track

    def shuffle_mode(self, value):
        if value is True:
            self.ordered_song_ids = list(self.song_ids)
            random.shuffle(self.song_ids)
            self.current_index = 0
        elif value is False:
            self.current_index = self.ordered_song_ids.index(
                self.song_ids[self.current_index])
            self.song_ids = self.ordered_song_ids

        return self.song_ids[self.current_index]

    def __str__(self):
        return "<Queue: length=%d position=%d items=%s>" % (len(self.song_ids), self.current_index, self.song_ids)
