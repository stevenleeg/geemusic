from flask import Response, stream_with_context, redirect
import requests
import boto3
from uuid import uuid4
from botocore.client import Config
from os import environ
from geemusic import app, api

BUCKET_NAME = environ.get("S3_BUCKET_NAME")

def proxy_response(req):
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))

    bucket = s3.Bucket(BUCKET_NAME)
    file_name = str(uuid4())

    app.debug = False
    obj = bucket.put_object(
            Key=file_name,
            Body = req.content,
            ACL="authenticated-read",
            ContentType=req.headers["content-type"]
          )
    
    app.debug = True
    
    url = s3_client.generate_presigned_url(
            "get_object", 
            Params = {
                "Bucket": BUCKET_NAME, 
                "Key"   : file_name},
            ExpiresIn=120
          )
    return redirect(url, 303)

@app.route('/wake-up')
def index():
	return 'I am not sleeping!'

@app.route("/alexa/stream/<song_id>")
def redirect_to_stream(song_id):
    stream_url = api.get_google_stream_url(song_id)
    # Scrobble if Last.fm is setup
    if environ.get('LAST_FM_ACTIVE'):
        from .utils import last_fm
        song_info = api.get_song_data(song_id)
        last_fm.scrobble(
            song_info['title'],
            song_info['artist'],
            environ['LAST_FM_SESSION_KEY']
        )

    app.logger.debug('URL is %s' % stream_url)
    req = requests.get(stream_url, stream=False)
    if environ.get('USE_S3_BUCKET') == "True":
        return proxy_response(req)
    return Response(stream_with_context(req.iter_content(chunk_size=1024 * 1024)), content_type=req.headers['content-type'])
