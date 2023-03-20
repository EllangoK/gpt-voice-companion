from colorama import Fore, Style, init
from .utils import ensure_dir_exists
from .openai_wrapper import OpenAI
from .elevenlabs import ElevenLabsTTS
from playaudio import playaudio
import logging
import time
import os

init(autoreset=True)  # Initialize colorama

class Companion:

    AUDIO_PATH = "audio/"
    CONVERSATION_PATH = "conversations/"

    def __init__(self, openai_key: str, elevenlabs_key: str, chatbot_name: str, openai_model: str = 'gpt-3.5-turbo', openai_temperature: int = 1.2, openai_max_reply_tokens: int = 4000, voice_id: str = None, quiet_logging: bool = True):
        with OpenAI(openai_key, chatbot_name, openai_model, openai_temperature, openai_max_reply_tokens) as openai:
            self.openai = openai
        self.elevenlabs = ElevenLabsTTS(elevenlabs_key, voice_id=voice_id)
        self.history = ""

        ensure_dir_exists(self.AUDIO_PATH)
        ensure_dir_exists(self.CONVERSATION_PATH)
    
        if quiet_logging:
            logging.basicConfig(level=logging.CRITICAL)
        else:
            logging.basicConfig(level=logging.DEBUG)

    def get_response(self, history: str, prompt: str) -> str:
        response = self.openai.query_gpt(history, prompt)
        logging.debug(f"Response: {response}")
        return response

    def say(self, text: str):
        success, audio_path = self.elevenlabs.write_audio(text, self.AUDIO_PATH)
        logging.debug(f"Audio path: {audio_path}")
        if success:
            print(Fore.BLUE + f"{self.openai.name}: " + Style.RESET_ALL + text)
            playaudio(audio_path)
        else:
            print(Fore.RED + "Error: " + Style.RESET_ALL + "Could not access ElevenLabs API.")

    def loop(self):
        print("Type !h for help")
        print(Fore.YELLOW + f"Context: " + Style.RESET_ALL + "You are talking to a chatbot named " + Fore.BLUE + self.openai.name + Style.RESET_ALL + f", prompted with \"{self.openai.context}\".")
        while True:
            text = input(Fore.GREEN + "You: " + Style.RESET_ALL)
            logging.debug(f"User input: {text}")

            if text.startswith("!"):
                if text[1].lower() == "q":
                    print("Exiting...")
                    break
                elif text[1].lower() == "h":
                    print("Commands:")
                    print("!q - quit")
                    print("!h - help")
                    continue

            response = self.get_response(self.history, text)
            if len(response.strip()) == 0:
                print(Fore.RED + "Error: " + Style.RESET_ALL + "No response from chatbot.")
                continue

            self.say(response)
            self.history += f"User: {text} \n{self.openai.name}: {response} \n"
            logging.debug(f"History: {self.history}")

            time.sleep(1)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.save_conversation()

    def save_conversation(self):
        date = time.strftime("%Y-%m-%d", time.localtime())
        folder_path = os.path.join(self.CONVERSATION_PATH, date)
        ensure_dir_exists(folder_path)
        path = os.path.join(folder_path, f"{str(int(time.time()))}.txt")
 
        with open(path, "w", encoding="utf8") as f:
            f.write(self.history)