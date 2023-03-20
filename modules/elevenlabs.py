import requests
import hashlib
import os
import time
import json

class ElevenLabsTTS:
    TTS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
    VOICES_URL = "https://api.elevenlabs.io/v1/voices"
    CONFIG_FILENAME = "config.json"

    def __init__(self, key: str, voice_id: str = None):
        self.key = key
        self.session = requests.Session()
        self.voice_id = voice_id

        self.load_config()
        
        self.tts_url = f"{self.TTS_BASE_URL}{self.voice_id}"

    def load_config(self):
        try:
            self.config = json.load(open(self.CONFIG_FILENAME))
        except FileNotFoundError:
            self.config = {}

        self.voice_id = self.voice_id or self.config.get('voice_id') or "EXAVITQu4vr4xnSDxMaL" # Premade ElevenLabs "Bella" Voice
        self.save_config()

    def save_config(self):
        self.config['voice_id'] = self.voice_id

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
    
    def get_voices(self):
        headers = {
            "accept": "application/json",
            "xi-api-key": self.key,
        }

        try:
            response = self.session.get(self.VOICES_URL, headers=headers)
            response.raise_for_status()
            voices = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching voices: {e}")
            return []

        return voices