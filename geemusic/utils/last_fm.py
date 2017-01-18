# Last.fm Syncing Tool
import os
import requests

def authorize():
    # TODO: Create function
    doNothing = True

def scrobble(song_name, artist_name):
    apiResp = requests.post('http://ws.audioscrobbler.com/2.0/', {'method': 'track.updateNowPlaying', 'apiKey': os.environ['LAST_FM_API'], 'track': song_name, 'artist': artist_name})
    print apiResp.text
