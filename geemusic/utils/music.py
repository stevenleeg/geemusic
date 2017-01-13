from os import environ
from gmusicapi import Mobileclient
import operator

class GMusicWrapper:
    def __init__(self, username, password):
        self._api = Mobileclient()
        success = self._api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

        if not success:
            raise Exception("Unsuccessful login. Aborting!")

    def _search(self, query_type, query):
        results = self._api.search(query)
        hits_key = "%s_hits" % query_type

        if hits_key not in results:
            return []

        # Ugh, Google had to make this schema nonstandard...
        if query_type == 'song':
            query_type = 'track'

        return map(lambda x: x[query_type], results[hits_key])

    def get_artist(self, name):
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

    def get_artist_album_list(self, artist_name):
        search = self._search("album", artist_name)
        album_list = "Here's the album listing for  %s: " % artist_name
        for index, val in enumerate(search):
            if search[index]['artist'].lower() != artist_name:
                search_by_album_id = self._api.get_album_info(album_id=search[index]['albumId'], include_tracks=True)
                if len(search_by_album_id['tracks']) > 4:
                    album_list += (search[index]['name'])
                    if index != 50:
                        album_list += ", "
        return album_list


    """
    latest album / oldest album
    same as above but have a dict with the year key,
    then sort based on a isLatest = true/false
    """

    # https: // still - earth - 66397.herokuapp.com / alexa
    @classmethod
    def generate_api(self):
        return self(environ['GOOGLE_EMAIL'], environ['GOOGLE_PASSWORD'])
