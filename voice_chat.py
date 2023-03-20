import os
import argparse
from dotenv import load_dotenv
from modules.companion import Companion

def load_keys_from_env():
    load_dotenv()
    return os.environ.get('OPENAI_API_KEY'), os.environ.get('ELEVENLABS_API_KEY')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Have GPT talk to you')
    parser.add_argument('--openai_key', help='Your OpenAI API key.')
    parser.add_argument('--elevenlabs_key', help='Your elevenlabs.io API key.')
    parser.add_argument('--quiet', action='store_true', help='disable logging', default=True)
    parser.add_argument('--name', help='Name of the chatbot (default is OpenAI)', default='OpenAI')
    parser.add_argument('--model', help='OpenAI model to use (default is gpt-3.5-turbo)', default='gpt-3.5-turbo')
    parser.add_argument('--temperature', help='OpenAI temperature to use (default is 1.2)', default=1.2)
    parser.add_argument('--max_reply_tokens', help='OpenAI max tokens to reply with (default is 200)', default=200)
    parser.add_argument('--voice_id', help='Voice ID for custom ElevenLabs model', default=None)
    parser.add_argument('--voice_recognition', action='store_true', help='Use voice input', default=True)
    parser.add_argument('--openai_retry_attempts', help='Number of times to retry OpenAI API calls (default is 3)', default=3)
    args = parser.parse_args()

    openai_key, elevenlabs_key = args.openai_key, args.elevenlabs_key

    if not openai_key or not elevenlabs_key:
        openai_key, elevenlabs_key = load_keys_from_env()
        if not openai_key or not elevenlabs_key:
            parser.print_help()
            exit(1)

    with Companion(openai_key, elevenlabs_key, args.voice_recognition, args.name, args.model, args.temperature, args.max_reply_tokens, args.openai_retry_attempts, args.voice_id, quiet_logging=args.quiet) as companion:
        companion.loop()