from app.services.event_emitter import EventEmitter
import json
import uuid
from collections import defaultdict


class StreamService(EventEmitter):
    def __init__(self, websocket):
        super().__init__()
        self.ws = websocket
        self.expected_audio_index = 0
        self.audio_buffer = defaultdict(str)
        self.stream_sid = ''

    def set_stream_sid(self, stream_sid):
        """Sets the stream session ID."""
        self.stream_sid = stream_sid

    def buffer(self, index, audio):
        """Buffers or sends audio based on the index."""
        if index is None:
            self.send_audio(audio)
        elif index == self.expected_audio_index:
            self.send_audio(audio)
            self.expected_audio_index += 1

            while self.expected_audio_index in self.audio_buffer:
                buffered_audio = self.audio_buffer.pop(self.expected_audio_index)
                self.send_audio(buffered_audio)
                self.expected_audio_index += 1
        else:
            self.audio_buffer[index] = audio

    def send_audio(self, audio):
        """Sends audio over WebSocket and emits 'audiosent' event."""
        try:
            self.ws.send(
                json.dumps({
                    'streamSid': self.stream_sid,
                    'event': 'media',
                    'media': {
                        'payload': audio,
                    },
                })
            )
            mark_label = self.generate_mark_label()
            self.ws.send(
                json.dumps({
                    'streamSid': self.stream_sid,
                    'event': 'mark',
                    'mark': {
                        'name': mark_label,
                    },
                })
            )
            print(f'Audio sent: {mark_label}')
            self.emit('audiosent', mark_label)
        except Exception as e:
            print(f"Error sending audio: {e}")

    def generate_mark_label(self):
        """Generates a unique mark label."""
        return str(uuid.uuid4())
