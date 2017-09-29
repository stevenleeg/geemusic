# Last.fm Syncing Tool
# Lean, fast, and functional
import os
import time
import datetime
import requests
import hashlib

from gmusicapi import CallFailure, Mobileclient

api_head = 'http://ws.audioscrobbler.com/2.0/'
secret = os.environ['LAST_FM_API_SECRET']

def authorize(user_token):
    params = {
            'api_key': os.environ['LAST_FM_API'],
            'method': 'auth.getSession',
            'token': user_token
            }
    requestHash = hashRequest(params, secret)
    params['api_sig'] = requestHash
    apiResp = requests.post(api_head, params)
    return apiResp.text

def nowPlaying(song_name, artist_name, session_key):
    params = {
            'method': 'track.updateNowPlaying',
            'api_key': os.environ['LAST_FM_API'],
            'track': song_name,
            'artist': artist_name,
            'sk': session_key
            }
    requestHash = hashRequest(params, secret)
    params['api_sig'] = requestHash
    apiResp = requests.post(api_head, params)
    return apiResp.text

def scrobble(song_name, artist_name, session_key):
    # Currently this sort of cheats the timestamp protocol
    params = {
            'method': 'track.scrobble',
            'api_key': os.environ['LAST_FM_API'],
            'timestamp': str( int( time.time() ) ),
            'track': song_name,
            'artist': artist_name,
            'sk': session_key
            }
    requestHash = hashRequest(params, secret)
    params['api_sig'] = requestHash
    apiResp = requests.post(api_head, params)
    return apiResp.text

def hashRequest(obj, secretKey):
    string = ''
    items = list(obj.keys())
    items.sort()
    for i in items:
        string += i
        string += obj[i]
    string += secretKey
    stringToHash = string.encode('utf8')
    m = hashlib.md5()
    m.update(stringToHash)
    requestHash = m.hexdigest()
    return requestHash
