import json
import requests
import openai
import logging

class OpenAI:
    CONFIG_FILENAME = 'config.json'

    def __init__(self, api_key: str, name:str, openai_model: str, temperature: float, max_reply_tokens: int):
        self.api_key = api_key
        self.name = name
        self.openai_model = openai_model
        self.temperature = temperature
        self.max_reply_tokens = max_reply_tokens

        self.load_config()

    def load_config(self):
        self.config = json.load(open(self.CONFIG_FILENAME))
        self.name = self.config.get('name', self.name)
        self.context = self.config.get('context', "You are an AI assistant. You are talking to a user.")
        self.openai_model = self.config.get('openai_model', self.openai_model)
        self.temperature = self.config.get('temperature', self.temperature)
        self.max_reply_tokens = self.config.get('max_reply_tokens', self.max_tokens)
        self.save_config()

    def save_config(self):
        self.config['name'] = self.name
        self.config['context'] = self.context
        self.config['openai_model'] = self.openai_model
        self.config['temperature'] = self.temperature
        self.config['max_reply_tokens'] = self.max_reply_tokens

        with open(self.CONFIG_FILENAME, 'w') as f:
            json.dump(self.config, f, indent=4)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.save_config()

    def extract_reply(self, response: str) -> str:
        try:
            return response.split(self.name + ": ")[1]
        except IndexError:
            return response

    def query_gpt(self, history: str, prompt: str) -> str:
        query = [{'role':'system', 'content': self.context}, {'role':'user', 'content': history + prompt}]
        logging.debug(f"Query: {query}")
        response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=query,
            temperature=self.temperature,
            max_tokens=self.max_reply_tokens,
            stop=["User:", f"{self.name}:"]
        )

        text = response['choices'][0]['message']['content']

        return self.extract_reply(text)