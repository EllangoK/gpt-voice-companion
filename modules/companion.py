import logging
import os
import time
from enum import Enum

import os
import speech_recognition as sr
import gradio as gr
from colorama import Fore, Style, init
from playaudio import playaudio

from .elevenlabs import ElevenLabsTTS
from .openai_wrapper import OpenAI
from .utils import ensure_dir_exists

init(autoreset=True)  # Initialize colorama


class Companion:

    AUDIO_PATH = "audio/"
    CONVERSATION_PATH = "conversations/"

    def __init__(self, openai_key: str, elevenlabs_key: str, voice_recognition: bool, chatbot_name: str, chatbot_context: str, openai_model, openai_temperature: int, openai_max_reply_tokens: int, openai_retry_attempts: int, voice_id: str, debug: bool = True):
        self.openai = OpenAI(openai_key, chatbot_name, chatbot_context, openai_model, openai_temperature, openai_max_reply_tokens, openai_retry_attempts)
        self.elevenlabs = ElevenLabsTTS(elevenlabs_key, voice_id=voice_id)
        self.voice_recognition = voice_recognition or True
        self.history = ""

        ensure_dir_exists(self.AUDIO_PATH)
        ensure_dir_exists(self.CONVERSATION_PATH)
    
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.CRITICAL)

    def get_response(self, prompt: str) -> str:
        response = self.openai.query_gpt(prompt)
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
                return ProcessStatus(ProcessInputStatus.EXIT, None)
            elif text.lower() == "help":
                return ProcessStatus(ProcessInputStatus.LOG, "Commands for voice input:\nexit - quit\nhelp - help")
        else:
            if text.startswith("!"):
                if text[1].lower() == "q":
                    return ProcessStatus(ProcessInputStatus.EXIT, None)
                elif text[1].lower() == "h":
                    return ProcessStatus(ProcessInputStatus.LOG, "Commands for text input:\n!q - quit\n!h - help")

        for attempt in range(retry_attempts + 1):
            response = self.get_response(self.history + text)
            if len(response.strip()) > 0:
                break
            if attempt == retry_attempts:
                return ProcessStatus(ProcessInputStatus.LOG, (Fore.RED + "Error: " + Style.RESET_ALL + "No response from chatbot."))
            logging.debug(f"Retry attempt {attempt + 1}")

        self.history += f"User: {text} \n{self.openai.name}: {response} \n"
        logging.debug(f"History: {self.history}")

        return ProcessStatus(ProcessInputStatus.SAY, response)

    def loop_text_input(self):
        while True:
            user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL)
            logging.debug(f"User input: {user_input}")

            status = self.process_input(user_input)
            if status.status == ProcessInputStatus.EXIT:
                break
            elif status.status == ProcessInputStatus.LOG:
                print(status.response)
            elif status.status == ProcessInputStatus.SAY:
                self.say(status.response)

    def loop_voice_input(self):
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    user_input = recognizer.recognize_google(audio)
                    logging.debug(f"Audio user input: {user_input}")
                    print(Fore.GREEN + "You: " + Style.RESET_ALL + user_input)
                except sr.UnknownValueError:
                    print(Fore.RED + "Error: " + Style.RESET_ALL + "Could not understand the audio.")
                    continue
                except sr.RequestError:
                    print(Fore.RED + "Error: " + Style.RESET_ALL + "Could not request results from Google Speech Recognition service.")
                    continue

            status = self.process_input(user_input, is_voice=True)
            if status.status == ProcessInputStatus.EXIT:
                break
            elif status.status == ProcessInputStatus.LOG:
                print(status.response)
            elif status.status == ProcessInputStatus.SAY:
                self.say(status.response)

    def launch_demo(self):
        with gr.Blocks() as demo:
            gr.Markdown(f"""## You are talking to a chatbot named {self.openai.name}, prompted with:
            \"{self.openai.context}\"""")
            chatbot = gr.Chatbot()
            msg = gr.Textbox()
            global exit_check
            exit_check = False
            with gr.Row():
                submit_btn = gr.Button("Submit")
                clear_btn = gr.Button("Clear")
                exit_btn = gr.Button("Exit")

            def user(user_message, chatbot_dialogue):
                return "", chatbot_dialogue + [[user_message, None]]

            def bot(chatbot_dialogue):
                status = self.process_input(chatbot_dialogue[-1][0])
                if status.status == ProcessInputStatus.EXIT:
                    pass
                elif status.status == ProcessInputStatus.LOG:
                    pass
                elif status.status == ProcessInputStatus.SAY:
                    self.say(status.response)
                chatbot_dialogue[-1][1] = status.response
                return chatbot_dialogue
            
            def clear_func():
                self.history = ""
                return None

            def exit():
                global exit_check
                exit_check = True
                print(Fore.RED + "Exiting..." + Style.RESET_ALL)
                return None

            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, chatbot, chatbot
            )
            submit_btn.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, chatbot, chatbot
            )
            clear_btn.click(fn=clear_func, inputs=None, outputs=chatbot, queue=False)
            exit_btn.click(fn=exit, inputs=None, outputs=None, queue=False)

        demo.launch(prevent_thread_lock=True)

        while not exit_check:
            time.sleep(0.5)

        demo.close()

    def loop(self, gui: bool = False):
        if gui:
            self.launch_demo()
        else:
            print("Type !h for help")
            print(Fore.YELLOW + f"Context: " + Style.RESET_ALL + "You are talking to a chatbot named " + Fore.BLUE + self.openai.name + Style.RESET_ALL + f", prompted with \"{self.openai.context}\".")

            if self.voice_recognition:
                self.loop_voice_input()
            else:
                self.loop_text_input()

    def get_voices(self):
        return self.elevenlabs.get_voices()

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

class ProcessInputStatus(Enum):
    SAY = 0
    LOG = 1
    EXIT = 2

class ProcessStatus:

    def __init__(self, status: ProcessInputStatus, data: str = None):
        self.status = status
        self.response = data
