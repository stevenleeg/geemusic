import random
from os import environ
import threading, traceback

from gmusicapi import CallFailure, Mobileclient

class GMusicWrapper:
    def __init__(self, username, password, logger=None):
        self._api = Mobileclient()
        self.logger = logger
        success = self._api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

        if not success:
            raise Exception("Unsuccessful login. Aborting!")

        # Populate our library
        self.library = {}
        self.indexing_thread = threading.Thread(
            target=self.index_library
        )
        self.indexing_thread.start()

    def _search(self, query_type, query):
        try:
            results = self._api.search(query)
        except CallFailure:
            return []

        hits_key = "%s_hits" % query_type

        if hits_key not in results:
            return []

        # Ugh, Google had to make this schema nonstandard...
        if query_type == 'song':
            query_type = 'track'

        return map(lambda x: x[query_type], results[hits_key])

    def is_indexing(self):
        return self.indexing_thread.is_alive()

    def index_library(self):
        """
        Downloads the a list of every track in a user's library and populates
        self.library with storeIds -> track definitions
        """
        self.logger.debug('Fetching library...')
        tracks = self.get_all_songs()

        for track in tracks:
            song_id = track['id']
            self.library[song_id] = track

        self.logger.debug('Done! Discovered %d tracks.' % len(self.library))

    def get_artist(self, name):
        """
        Fetches information about an artist given its name
        """
        search = self._search("artist", name)

        if len(search) == 0:
            return False

        return self._api.get_artist_info(search[0]['artistId'], max_top_tracks=100)

    def get_album(self, name, artist_name=None):
        if artist_name:
            name = "%s %s" % (name, artist_name)

        search = self._search("album", name)

        if len(search) == 0:
            return False

        return self._api.get_album_info(search[0]['albumId'])

    def get_latest_album(self, artist_name=None):
        search = self._search("artist", artist_name)

        if len(search) == 0:
            return False

        artist_info = self._api.get_artist_info(search[0]['artistId'], include_albums=True)
        album_info = artist_info['albums']
        sorted_list = sorted(album_info.__iter__(), key=lambda s: s['year'], reverse=True)

        for index, val in enumerate(sorted_list):
            album_info = self._api.get_album_info(album_id=sorted_list[index]['albumId'], include_tracks=True)
            if len(album_info['tracks']) >= 5:
                return album_info

        return False

    def get_album_by_artist(self, artist_name, album_id=None):
        search = self._search("artist", artist_name)
        if len(search) == 0:
            return False

        artist_info = self._api.get_artist_info(search[0]['artistId'], include_albums=True)
        album_info = artist_info['albums']
        random.shuffle(album_info)

        for index, val in enumerate(album_info):
            album = self._api.get_album_info(album_id=album_info[index]['albumId'], include_tracks=True)
            if album['albumId'] != album_id:
                if len(album['tracks']) >= 5:
                    return album

        return False



    def get_song(self, name, artist_name=None):
        if artist_name:
            name = "%s %s" % (artist_name, name)

        search = self._search("song", name)

        if len(search) == 0:
            return False

        return search[0]

    def get_station(self, title, artist_id=None):
        if artist_id != None:
            return self._api.create_station(title, artist_id=artist_id)

    def get_station_tracks(self, station_id):
        return self._api.get_station_tracks(station_id)

    def get_google_stream_url(self, song_id):
        return self._api.get_stream_url(song_id)

    def get_stream_url(self, song_id):
        return "%s/stream/%s" % (environ['APP_URL'], song_id)

    def get_all_user_playlist_contents(self):
        return self._api.get_all_user_playlist_contents()

    def get_all_songs(self):
        return self._api.get_all_songs()

    def rate_song(self, song, rating):
        return self._api.rate_songs(song, rating)

    def extract_track_info(self, track):
        # When coming from a playlist, track info is nested under the "track"
        # key
        if 'track' in track:
            track = track['track']

        if 'storeId' in track:
            return (track, track['storeId'])
        elif 'trackId' in track:
            return (self.library[track['trackId']], track['trackId'])
        else:
            return (None, None)

    def get_artist_album_list(self, artist_name):
        search = self._search("artist", artist_name)
        if len(search) == 0:
            return False

        artist_info = self._api.get_artist_info(search[0]['artistId'], include_albums=True)
        album_list_text = "Here's the album listing for %s: " % artist_name

        counter = 0
        for index, val in enumerate(artist_info['albums']):
            if counter > 25:  # alexa will time out if the list takes too long to iterate through
                break
            album_info = self._api.get_album_info(album_id=artist_info['albums'][index]['albumId'], include_tracks=True)
            if len(album_info['tracks']) > 5:
                counter += 1
                album_list_text += (artist_info['albums'][index]['name']) + ", "
        return album_list_text

    def get_latest_artist_albums(self, artist_name):
        search = self._search("artist", artist_name)

        if len(search) == 0:
            return False

        artist_info = self._api.get_artist_info(search[0]['artistId'], include_albums=True)
        album_list = artist_info['albums']

        sorted_list = sorted(album_list.__iter__(), key=lambda s: s['year'], reverse=True)

        speech_text = 'The latest albums by %s are ' % artist_name

        counter = 0
        for index, val in enumerate(sorted_list):
            if counter > 5:
                break
            else:
                album_info = self._api.get_album_info(album_id=sorted_list[index]['albumId'], include_tracks=True)
                if len(album_info['tracks']) >= 5:
                    counter += 1
                    album_name = sorted_list[index]['name']
                    album_year = sorted_list[index]['year']
                    speech_text += '%s, released in %d, ' % (album_name, album_year)

        return speech_text

    @classmethod
    def generate_api(cls, **kwargs):
        return cls(environ['GOOGLE_EMAIL'], environ['GOOGLE_PASSWORD'], **kwargs)
