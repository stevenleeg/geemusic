import unittest
import json
import uuid

from os import getenv
from geemusic import app, ask
from flask_ask import audio

play_request = {
  "version": "1.0",
  "session": {
    "new": True,
    "sessionId": "amzn1.echo-api.session.0000000-0000-0000-0000-00000000000",
    "application": {
      "applicationId": "fake-application-id"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.account.AM3B00000000000000000000000"
    }
  },
  "context": {
    "System": {
      "application": {
        "applicationId": "fake-application-id"
      },
      "user": {
        "userId": "amzn1.account.AM3B00000000000000000000000"
      },
      "device": {
        "supportedInterfaces": {
          "AudioPlayer": {}
        }
      }
    },
    "AudioPlayer": {
      "offsetInMilliseconds": 0,
      "playerActivity": "IDLE"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "string",
    "timestamp": "string",
    "locale": "string",
    "intent": {
      "name": "TestPlay",
      "slots": {
        }
      }
    }
}


class AudioIntegrationTests(unittest.TestCase):
    """ Integration tests of the Audio Directives """

    def setUp(self):
        self.app = app
        self.ask = ask
        self.client = self.app.test_client()
        self.stream_url = getenv('APP_URL')
        self.custom_token = 'custom_uuid_{0}'.format(str(uuid.uuid4()))

        @self.ask.intent('TestPlay')
        def play():
            return audio('playing').play(self.stream_url)

        @self.ask.intent('TestCustomTokenIntents')
        def custom_token_intents():
            return audio('playing with custom token').play(self.stream_url, 
                                                           opaque_token=self.custom_token)

    def tearDown(self):
        pass

    def test_play_intent(self):
        """ Test to see if we can properly play a stream """
        response = self.client.post('/alexa', data=json.dumps(play_request))
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual('playing',
                         data['response']['outputSpeech']['text'])

        directive = data['response']['directives'][0]
        self.assertEqual('AudioPlayer.Play', directive['type'])

        stream = directive['audioItem']['stream']
        self.assertIsNotNone(stream['token'])
        self.assertEqual(self.stream_url, stream['url'])
        self.assertEqual(0, stream['offsetInMilliseconds'])

    def test_play_intent_with_custom_token(self):
        """ Test to check that custom token supplied is returned """

        # change the intent name to route to our custom token for play_request
        original_intent_name = play_request['request']['intent']['name']
        play_request['request']['intent']['name'] = 'TestCustomTokenIntents'

        response = self.client.post('/alexa', data=json.dumps(play_request))
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual('playing with custom token',
                         data['response']['outputSpeech']['text'])

        directive = data['response']['directives'][0]
        self.assertEqual('AudioPlayer.Play', directive['type'])

        stream = directive['audioItem']['stream']
        self.assertEqual(stream['token'], self.custom_token)
        self.assertEqual(self.stream_url, stream['url'])
        self.assertEqual(0, stream['offsetInMilliseconds'])

        # reset our play_request
        play_request['request']['intent']['name'] = original_intent_name

    def test_play_some_music_intent(self):
        """ Test that play some music intent works """
        
        psm_pr = play_request
        psm_pr['request']['intent']['name'] = 'GeeMusicPlayIFLRadioIntent'

        response = self.client.post('/alexa', data=json.dumps(play_request))
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual('Playing music from your personalized station.',
                         data['response']['outputSpeech']['text'])
        
        directive = data['response']['directives'][0]
        self.assertEqual('AudioPlayer.Play', directive['type'])
        
        stream = directive['audioItem']['stream']
        stream_token = stream['url'].split('/')[-1]
        self.assertIsNotNone(stream['token'])
        self.assertIn(self.stream_url , stream['url'])
        self.assertEqual('stream', stream['url'].split('/')[-2]) 
        self.assertIsNotNone(stream_token)
        self.assertNotEqual(stream_token, '')
        self.assertEqual(0, stream['offsetInMilliseconds'])


if __name__ == '__main__':
    unittest.main()
