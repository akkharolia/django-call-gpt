import json
from channels.generic.websocket import WebsocketConsumer
from app.services.gpt import GPTService
from app.services.stream import StreamService
from app.services.transcription import TranscriptionService
from app.services.tts import TextToSpeechService
from app.services.gpt_prompt import WELCOME_MSG


class WsConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpt_service = GPTService(self)
        self.stream_service = StreamService(self)
        self.transcription_service = TranscriptionService()
        self.tts_service = TextToSpeechService()

        self.stream_sid = ''
        self.call_sid = ''
        self.marks = []
        self.interaction_count = 0

        # Set up event listeners
        self.transcription_service.on('utterance', self.handle_utterance)
        self.transcription_service.on('transcription', self.handle_transcription)
        self.gpt_service.on('gptreply', self.handle_gptreply)
        self.tts_service.on('speech', self.handle_speech)
        self.stream_service.on('audiosent', self.handle_audio_sent)

    def connect(self):
        self.accept()

    def disconnect(self, *args):
        self.close()

    def handle_utterance(self, text):
        if len(self.marks) and len(text) > 5:
            print('Twilio -> Interruption, Clearing stream')
            self.send(text_data=json.dumps({
                'streamSid': self.stream_sid,
                'event': 'clear'
            }))

    def handle_transcription(self, text):
        if not text:
            return ''
        print(f'Interaction {self.interaction_count} - STT -> {text}')
        self.gpt_service.completion(text, self.interaction_count, 'user', 'user', self.call_sid)
        self.interaction_count += 1
    
    def handle_gptreply(self, gpt_reply, icount):
        print(f'Interaction {icount}: GPT -> TTS {gpt_reply["partial_response"]}')
        self.tts_service.generate(gpt_reply, icount)

    def handle_audio_sent(self, marklabel):
        self.marks.append(marklabel)

    def handle_speech(self, response_index, audio, label, icount=0):
        self.stream_service.buffer(response_index, audio)

    def receive(self, text_data):
        msg = json.loads(text_data)
        event = msg.get('event')
        
        if event == 'start':
            self.stream_sid = msg['start']['streamSid']
            self.call_sid = msg['start']['callSid']

            self.stream_service.set_stream_sid(self.stream_sid)
            self.gpt_service.set_call_sid(self.call_sid)
            self.tts_service.generate({'partial_response_index': None, 'partial_response': WELCOME_MSG}, 0)

        elif event == 'media':
            payload = msg['media']['payload']
            self.transcription_service.send(payload)

        elif event == 'mark':
            label = msg['mark']['name']
            print(f'Twilio -> Starting Media Stream for {msg["sequenceNumber"]}')
            self.marks = [m for m in self.marks if m != label]

        elif event == 'stop':
            print(f'Twilio -> Media stream {self.stream_sid} ended.')
