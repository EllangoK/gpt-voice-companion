import hashlib
import json
import os
import time

import requests

from modules.config_manager import ConfigManager

from .utils import ensure_dir_exists


class ElevenLabsTTS:
    TTS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
    VOICES_URL = "https://api.elevenlabs.io/v1/voices"

    DEFAULTS = {
       'voice_id': "EXAVITQu4vr4xnSDxMaL"  # Premade ElevenLabs "Bella" Voice
    }

    def __init__(self, env: dict):
        self.config_manager = ConfigManager(env, self.DEFAULTS)
        self.load_config()
        self.session = requests.Session()
        
        self.tts_url = f"{self.TTS_BASE_URL}{self.voice_id}"

    def load_config(self):
        self.elevenlabs_api_key = self.config_manager['elevenlabs_api_key']
        self.voice_id = self.config_manager['voice_id']
        self.save_config()

    def save_config(self):
        self.config_manager['elevenlabs_api_key'] = self.elevenlabs_api_key
        self.config_manager['voice_id'] = self.voice_id

    def write_audio(self, text: str, base_path: str) -> tuple[bool, str|None]:
        data = {"text": text}
        headers = {
            "accept": "audio/mpeg",
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(self.tts_url, data=json.dumps(data), headers=headers, timeout=60)
            response.raise_for_status()
            filename = f"{hashlib.sha256((text + str(time.time())).encode('utf-8')).hexdigest()[:10]}.mp3"
            date = time.strftime("%Y-%m-%d", time.localtime())
            folder_path = os.path.join(base_path, date)
            path = os.path.join(folder_path, filename)
            ensure_dir_exists(folder_path)
            with open(path, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Error generating speech: {e}")
            return False, None

        return True, os.path.abspath(path)
    
    def get_voices(self):
        headers = {
            "accept": "application/json",
            "xi-api-key": self.elevenlabs_api_key,
        }

        try:
            response = self.session.get(self.VOICES_URL, headers=headers)
            response.raise_for_status()
            voices = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching voices: {e}")
            return []

        return voices
