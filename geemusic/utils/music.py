from gmusicapi import Mobileclient

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

        return map(lambda x: x[query_type], results[hits_key])

    def get_artist(self, name):
        search = self._search("artist", name)

        if len(search) == 0:
            return False

        return self._api.get_artist_info(search[0]['artistId'])

    def get_album(self, name, artist_name=None):
        if artist_name:
            name = "%s %s" % (name, artist_name)

        search = self._search("album", name)

        if len(search) == 0:
            return False

        return self._api.get_album_info(search[0]['albumId'])

    def get_stream_url(self, song_id):
        return self._api.get_stream_url(song_id)

