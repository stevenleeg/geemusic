from builtins import object, super
from flask_ask import context
import random


class MusicQueue(object):
    def __init__(self, api, tracks=[]):
        self.queues = {}
        self.api = api

    def __setattr__(self, name, value):
        if name == 'queues' or name == 'api':
            super().__setattr__(name, value)
        else:
            return self.get_or_create_queue(context.System.device.deviceId).__setattr__(name, value)

    def __hasattr__(self, name):
        if name == 'queues' or name == 'api':
            return super().__hasattr__(name)
        else:
            return self.get_or_create_queue(context.System.device.deviceId).__hasattr__(name)

    def __getattr__(self, name):
        if name == 'queues' or name == 'api':
            return super().__getattr__(name)
        else:
            return self.get_or_create_queue(context.System.device.deviceId).__getattribute__(name)  # object methods don't have __getattr__

    def get_or_create_queue(self, queue_id):
        if not queue_id in self.queues:
            self.queues[queue_id] = MusicQueueInternal(self.api)
        return self.queues[queue_id]

    def next(self):
        return self.get_or_create_queue(context.System.device.deviceId).next()

    def up_next(self):
        return self.get_or_create_queue(context.System.device.deviceId).up_next()

    def prev(self):
        return self.get_or_create_queue(context.System.device.deviceId).prev()

    def current(self):
        return self.get_or_create_queue(context.System.device.deviceId).current()

    def current_track(self):
        return self.get_or_create_queue(context.System.device.deviceId).current_track()

    def reset(self, tracks=[]):
        return self.get_or_create_queue(context.System.device.deviceId).reset(tracks)

    def enqueue_track(self, song):
        return self.get_or_create_queue(context.System.device.deviceId).enqueue_track(song)

    def shuffle_mode(self, value):
        return self.get_or_create_queue(context.System.device.deviceId).shuffle_mode(value)

    def loop_mode(self, value):
        return self.get_or_create_queue(context.System.device.deviceId).loop_mode(value)

    def __str__(self):
        return self.get_or_create_queue(context.System.device.deviceId).__str__()


class MusicQueueInternal(object):
    def __init__(self, api, tracks=[]):
        self.reset(tracks)
        self.current_index = 0
        self.api = api
        self.use_store = self.api.use_store

    def next(self):
        if self.current():
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

    def enqueue_track(self, song):
        if self.use_store:
            song_id = song['storeId']
        else:
            song_id = song['id']
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
