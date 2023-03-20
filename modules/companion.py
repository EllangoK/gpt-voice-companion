from colorama import Fore, Style, init
from .utils import ensure_dir_exists
from .openai_wrapper import OpenAI
from .elevenlabs import ElevenLabsTTS
from playaudio import playaudio
import logging
import time
import os
import speech_recognition as sr

init(autoreset=True)  # Initialize colorama

class Companion:

    AUDIO_PATH = "audio/"
    CONVERSATION_PATH = "conversations/"

    def __init__(self, openai_key: str, elevenlabs_key: str, voice_recognition: bool, chatbot_name: str, chatbot_context: str, openai_model: str = 'gpt-3.5-turbo', openai_temperature: int = 1.2, openai_max_reply_tokens: int = 4000, openai_retry_attempts: int = 3, voice_id: str = None, debug: bool = True):
        self.openai = OpenAI(openai_key, chatbot_name, chatbot_context, openai_model, openai_temperature, openai_max_reply_tokens, openai_retry_attempts)
        self.elevenlabs = ElevenLabsTTS(elevenlabs_key, voice_id=voice_id)
        self.voice_recognition = voice_recognition
        self.history = ""

        ensure_dir_exists(self.AUDIO_PATH)
        ensure_dir_exists(self.CONVERSATION_PATH)
    
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.CRITICAL)

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

    def process_input(self, text: str, is_voice: bool = False, retry_attempts: int = 3):
        if is_voice:
            if text.lower() == "exit":
                return False
            elif text.lower() == "help":
                print("Commands for voice input:")
                print("exit - quit")
                print("help - help")
                return True
        else:
            if text.startswith("!"):
                if text[1].lower() == "q":
                    return False
                elif text[1].lower() == "h":
                    print("Commands for text input:")
                    print("!q - quit")
                    print("!h - help")
                    return True

        for attempt in range(retry_attempts + 1):
            response = self.get_response(self.history, text)
            if len(response.strip()) > 0:
                break
            if attempt == retry_attempts:
                print(Fore.RED + "Error: " + Style.RESET_ALL + "No response from chatbot.")
                return True
            logging.debug(f"Retry attempt {attempt + 1}")

        self.say(response)
        self.history += f"User: {text} \n{self.openai.name}: {response} \n"
        logging.debug(f"History: {self.history}")

        time.sleep(2)
        return True

    def loop_text_input(self):
        while True:
            text = input(Fore.GREEN + "You: " + Style.RESET_ALL)
            logging.debug(f"User input: {text}")
            if not self.process_input(text):
                break

    def loop_voice_input(self):
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    print(Fore.GREEN + "You: " + Style.RESET_ALL + text)
                except sr.UnknownValueError:
                    print(Fore.RED + "Error: " + Style.RESET_ALL + "Could not understand the audio.")
                    continue
                except sr.RequestError:
                    print(Fore.RED + "Error: " + Style.RESET_ALL + "Could not request results from Google Speech Recognition service.")
                    continue
            if not self.process_input(text, is_voice=True):
                break

    def loop(self):
        print("Type !h for help")
        print(Fore.YELLOW + f"Context: " + Style.RESET_ALL + "You are talking to a chatbot named " + Fore.BLUE + self.openai.name + Style.RESET_ALL + f", prompted with \"{self.openai.context}\".")

        if self.voice_recognition:
            self.loop_voice_input()
        else:
            self.loop_text_input()

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