import json
import logging
from enum import Enum

import openai

from modules.config_manager import ConfigManager


class OpenAI:

    DEFAULTS = {
        'name': "OpenAI",
        'context': "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.",
        'openai_model': "gpt-3.5-turbo",
        'openai_temperature': 1.2,
        'openai_max_reply_tokens': 200,
        'openai_retry_attempts': 3
    }

    def __init__(self, args_dict: dict):
        self.config_manager = ConfigManager(args_dict, self.DEFAULTS)
        self.load_config()
        openai.api_key = self.openai_api_key

    def load_config(self):
        self.name = self.config_manager['name']
        self.context = self.config_manager['context']
        self.openai_model = self.config_manager['openai_model']
        self.openai_temperature = self.config_manager['openai_temperature']
        self.openai_max_reply_tokens = self.config_manager['openai_max_reply_tokens']
        self.openai_retry_attempts = self.config_manager['openai_retry_attempts']
        self.openai_api_key = self.config_manager['openai_api_key']
        self.save_config()

    def save_config(self):
        self.config_manager['name'] = self.name
        self.config_manager['context'] = self.context
        self.config_manager['openai_model'] = self.openai_model
        self.config_manager['openai_temperature'] = self.openai_temperature
        self.config_manager['openai_max_reply_tokens'] = self.openai_max_reply_tokens
        self.config_manager['openai_retry_attempts'] = self.openai_retry_attempts
        self.config_manager['openai_api_key'] = self.openai_api_key

    def extract_reply(self, response: str) -> str:
        try:
            return response.split(self.name + ": ")[1]
        except IndexError:
            return response

    def query_gpt(self, prompt: str) -> str:
        query = [{'role':'system', 'content': self.context}, {'role':'user', 'content': prompt}]
        logging.debug(f"Query: {query}")
        response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=query,
            temperature=self.openai_temperature,
            max_tokens=self.openai_max_reply_tokens,
            stop=["User:", f"{self.name}:"]
        )

        text = response['choices'][0]['message']['content']

        return self.extract_reply(text)
    
    def list_models(self):
        return openai.Model.list()