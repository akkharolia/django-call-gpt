import json
import base64
import requests
import traceback
from .event_emitter import EventEmitter
from django.conf import settings
from app.common import deepgram_client
from deepgram import SpeakOptions

class TextToSpeechService(EventEmitter):

    def __init__(self):
        super().__init__()
        self.next_expected_index = 0
        self.speech_buffer = {}
        self.dg_client = deepgram_client()
        

    def generate(self, gpt_reply, interaction_count):
        partial_response_index = gpt_reply['partial_response_index']
        partial_response = gpt_reply['partial_response']
        
        if not partial_response:
            return ''
        options = SpeakOptions(
            model=settings.VOICE_MODEL,
        )
        
        try:
            response = requests.post(
                url=f'https://api.deepgram.com/v1/speak?model={settings.VOICE_MODEL}&encoding=mulaw&sample_rate=8000&container=none',
                headers={
                    'Authorization': f'Token {settings.DEEPGRAM_KEY}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'text':partial_response
                })   
            )
            if response.status_code == 200:
                try:
                    blob = response.content
                    base64_string = base64.b64encode(blob).decode('utf-8')
                    self.emit('speech', partial_response_index, base64_string, partial_response, interaction_count)
                except Exception as err:
                    print('Deepgram TTS error', '\n', traceback.format_exc())

        except Exception as e:
            print('Error occurred in TextToSpeech service', '\n', traceback.format_exc())


        