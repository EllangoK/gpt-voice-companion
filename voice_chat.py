import argparse
import os

from dotenv import load_dotenv

from modules.companion import Companion


def load_keys_from_env():
    load_dotenv()
    return os.environ.get('OPENAI_API_KEY'), os.environ.get('ELEVENLABS_API_KEY')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Have GPT talk to you')
    parser.add_argument('--openai_key', help='Your OpenAI API key.')
    parser.add_argument('--elevenlabs_key', help='Your elevenlabs.io API key.')
    parser.add_argument('--debug', action='store_true', help='enable logging', default=False)
    parser.add_argument('--name', help='Name of the chatbot (default is OpenAI)')
    parser.add_argument('--context', help='Context to start the conversation with (default is "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.")')
    parser.add_argument('--model', help='OpenAI model to use (default is gpt-3.5-turbo)')
    parser.add_argument('--temperature', help='OpenAI temperature to use (default is 1.2)')
    parser.add_argument('--max_reply_tokens', help='OpenAI max tokens to reply with (default is 200)')
    parser.add_argument('--voice_id', help='Voice ID for custom ElevenLabs model (default is c, Bella Premade Voice)')
    parser.add_argument('--voice_recognition', help='Enable voice input')
    parser.add_argument('--openai_retry_attempts', help='Number of times to retry OpenAI API calls (default is 3)')
    parser.add_argument('--gui', action='store_true', help='Enable GUI (default is False)', default=False)
    args = parser.parse_args()

    openai_key, elevenlabs_key = args.openai_key, args.elevenlabs_key

    if not openai_key or not elevenlabs_key:
        openai_key, elevenlabs_key = load_keys_from_env()
        if not openai_key or not elevenlabs_key:
            parser.print_help()
            exit(1)

    with Companion(openai_key, elevenlabs_key, args.voice_recognition, args.name, args.context, args.model, args.temperature, args.max_reply_tokens, args.openai_retry_attempts, args.voice_id, debug=args.debug) as companion:
        companion.loop(gui=args.gui)
