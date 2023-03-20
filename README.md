# GPT Voice Companion

GPT Voice Companion is an interactive chatbot leveraging OpenAI's GPT models and ElevenLabs TTS (Text-to-Speech) to create a seamless and engaging conversational experience. It supports both voice and text input, while providing responses through a natural-sounding ElevenLabs voice.

![_image_](example.png)

To use this application, API access for both OpenAI and ElevenLabs is required.

# Installing 

1. Ensure you have Python installed. Then, install the required dependencies by running the following command:

        pip install -r requirements.txt

# Use

You can start the chatbot by running the following command:

    python voice_chat.py --openai_key <openapi_key> --elevenlabs_key <elevenlabs_key>

Alternatively, copy the .template.env file, rename it to .env, and fill in the API keys. Now, you can run the chatbot using:

    python voice_chat.py

You can modify the settings by either passing them as command-line arguments or by updating the config.json file (recommended). The configuration file is created and updated after the first run.

For example, to change the chatbot's name and use a custom voice, run the following command:

    python voice_chat.py --voice_id ZNJg5cGJHflCKVhOKpjQ --name Ivy

To view available options and settings, run:

    python voice_chat.py -h

# Features

- Voice and text input support
- Customizable context for the chatbot
- Ability to name the chatbot and adjust various parameters
- Retry attempts for OpenAI API calls in case of errors or empty responses
- Audio and conversations are automatically saved in a designated folder