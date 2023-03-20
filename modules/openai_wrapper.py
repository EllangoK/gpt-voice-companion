import json
import openai
import logging

class OpenAI:
    CONFIG_FILENAME = 'config.json'

    def __init__(self, api_key: str, name: str, context: str, openai_model: str, temperature: float, max_reply_tokens: int, retry_attempts: int):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.name = name
        self.context = context
        self.openai_model = openai_model
        self.temperature = temperature
        self.max_reply_tokens = max_reply_tokens
        self.retry_attempts = retry_attempts

        self.load_config()

    def load_config(self):
        try:
            self.config = json.load(open(self.CONFIG_FILENAME))
        except FileNotFoundError:
            self.config = {}

        self.name = self.name or self.config.get('name') or "OpenAI"
        self.context = self.context or self.config.get('context') or "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."
        self.openai_model = self.openai_model or self.config.get('openai_model') or "gpt-3.5-turbo"
        self.temperature = self.temperature or self.config.get('temperature') or 1.2
        self.max_reply_tokens = self.max_reply_tokens or self.config.get('max_reply_tokens') or 200
        self.retry_attempts = self.retry_attempts or self.config.get('retry_attempts') or 3
        self.save_config()

    def save_config(self):
        self.config['name'] = self.name
        self.config['context'] = self.context
        self.config['openai_model'] = self.openai_model
        self.config['temperature'] = self.temperature
        self.config['max_reply_tokens'] = self.max_reply_tokens
        self.config['retry_attempts'] = self.retry_attempts

        with open(self.CONFIG_FILENAME, 'w') as f:
            json.dump(self.config, f, indent=4)

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