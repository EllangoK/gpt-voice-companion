import requests
import hashlib
import os
import time
import json

class ElevenLabsTTS:
    BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
    VOICE_ID = "EXAVITQu4vr4xnSDxMaL" # Premade ElevenLabs "Bella" Voice
    CONFIG_FILENAME = "config.json"

    def __init__(self, key: str, voice_id: str = None):
        self.key = key
        self.session = requests.Session()
        self.VOICE_ID = voice_id if voice_id else self.VOICE_ID
        self.tts_url = f"{self.BASE_URL}{self.VOICE_ID}"

        self.load_config()

    def load_config(self):
        try:
            self.config = json.load(open(self.CONFIG_FILENAME))
        except FileNotFoundError:
            self.config = {}

        self.save_config()
        self.VOICE_ID = self.config.get('voice_id', self.VOICE_ID)
        self.save_config()

    def save_config(self):
        self.config['voice_id'] = self.VOICE_ID

        with open(self.CONFIG_FILENAME, 'w') as f:
            json.dump(self.config, f, indent=4)

    def write_audio(self, text: str, base_path: str) -> tuple[bool, str|None]:
        data = {"text": text}
        headers = {
            "accept": "audio/mpeg",
            "xi-api-key": self.key,
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(self.tts_url, data=json.dumps(data), headers=headers, timeout=60)
            response.raise_for_status()
            filename = f"{hashlib.sha256((text + str(time.time())).encode('utf-8')).hexdigest()[:10]}.mp3"
            path = os.path.join(base_path, filename)
            with open(path, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Error generating speech: {e}")
            return False, None

        return True, path