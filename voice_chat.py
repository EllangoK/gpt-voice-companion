import argparse
import os

from dotenv import load_dotenv

from modules.companion import Companion


def load_keys_from_env():
    load_dotenv()
    return os.environ.get('OPENAI_API_KEY'), os.environ.get('ELEVENLABS_API_KEY')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Have GPT talk to you')
    parser.add_argument('--openai_api_key', help='Your OpenAI API key.')
    parser.add_argument('--elevenlabs_api_key', help='Your elevenlabs.io API key.')
    parser.add_argument('--debug', action='store_true', help='enable logging', default=False)
    parser.add_argument('--name', help='Name of the chatbot (default is OpenAI)')
    parser.add_argument('--context', help='Context to start the conversation with (default is "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.")')
    parser.add_argument('--openai_model', help='OpenAI model to use (default is gpt-3.5-turbo)')
    parser.add_argument('--openai_temperature', help='OpenAI temperature to use (default is 1.2)')
    parser.add_argument('--openai_max_reply_tokens', help='OpenAI max tokens to reply with (default is 200)', type=int)
    parser.add_argument('--voice_id', help='Voice ID for custom ElevenLabs model (default is c, Bella Premade Voice)')
    parser.add_argument('--voice_recognition', help='Enable voice input')
    parser.add_argument('--openai_retry_attempts', help='Number of times to retry OpenAI API calls (default is 3)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gui', action='store_true', help='Enable the GUI', default=True)
    group.add_argument('--no-gui', dest='gui', action='store_false', help='Disable the GUI')
    args = parser.parse_args()

    openai_api_key, elevenlabs_api_key = args.openai_api_key, args.elevenlabs_api_key
    env_dict = vars(args)

    if not openai_api_key or not elevenlabs_api_key:
        openai_api_key, elevenlabs_api_key = load_keys_from_env()
        if not openai_api_key or not elevenlabs_api_key:
            parser.print_help()
            exit(1)
        env_dict['openai_api_key'] = openai_api_key
        env_dict['elevenlabs_api_key'] = elevenlabs_api_key

    with Companion(env_dict, debug=args.debug) as companion:
        companion.loop()
