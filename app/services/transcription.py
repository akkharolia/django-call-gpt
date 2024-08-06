import base64
from app.common import deepgram_client
from app.services.event_emitter import EventEmitter
from deepgram import LiveOptions, LiveTranscriptionEvents, DeepgramClientOptions, LiveResultResponse

class TranscriptionService(EventEmitter):
    def __init__(self):
        super().__init__()
        try:
            self.cl_options = DeepgramClientOptions(options={"keepalive": "true"})
            self.dg_client = deepgram_client()
            self.final_result = ''
            self.speech_final = False
            self.dg_connection = self.dg_client.listen.websocket.v('1')
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
            self.dg_connection.on(LiveTranscriptionEvents.SpeechStarted, self.on_metadata)
            self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
            self.dg_connection.on(LiveTranscriptionEvents.Close, self.on_close)
            options = LiveOptions(
                encoding='mulaw',
                sample_rate=8000,
                model='nova-2',
                punctuate=True,
                interim_results=True,
                endpointing=200,
                utterance_end_ms=1000
            )
            self.dg_connection.start(options)
        except Exception as e:
            print(f"Could not open deepgram socket: {e}")

    def on_metadata(self, speech=None, metadata=None, **kwargs):
        """Handles metadata events."""
        print(f"\n\n{speech} \n {metadata}\n\n")

    def on_close(self, closed1, closed, *args, **kwargs):
        """Handles close events."""
        print(f"\n\nDeepgram connection {closed} {args}\n\n")

    def on_message(self, result1, result: LiveResultResponse, *args, **kwargs):
        """Handles incoming messages and processes transcripts."""
        text = ""
        if len(result.channel.alternatives):
            text = result.channel.alternatives[0].transcript
        if not text:
            return
        
        if result.type == 'UtteranceEnd':
            if not self.speech_final:
                print(f"UtteranceEnd received before speechFinal, emit the text collected so far: {self.final_result}")
                self.emit_transcription(self.final_result)
                self.final_result = ''  # Reset final result
                return
            else:
                print('STT -> Speech was already final when UtteranceEnd received')
                return

        if result.is_final and text.strip():
            self.final_result += f" {text}"
            if result.speech_final:
                self.speech_final = True
                self.emit_transcription(self.final_result)
                self.final_result = ''  # Reset final result
            else:
                self.speech_final = False
        else:
            self.emit_utterance(text)

    def on_error(self, error1, error, **kwargs):
        """Handles error events."""
        print('STT -> Deepgram error')
        print(error)

    def handle_close(self, *args, **kwargs):
        """Handles close events."""
        print('STT -> Deepgram connection closed')

    def emit_transcription(self, text, *args, **kwargs):
        """Emits transcription events."""
        print(f'Transcription: {text}')
        self.emit('transcription', text)

    def emit_utterance(self, text, *args, **kwargs):
        """Emits utterance events."""
        print(f'Utterance: {text}')
        self.emit('utterance', text)

    def send(self, payload, *args, **kwargs):
        """Sends payload to Deepgram."""
        decoded_payload = base64.b64decode(payload)
        self.dg_connection.send(decoded_payload)
