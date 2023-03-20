# GPT Voice Companion

A simple bot that allows you to converse with OpenAI's GPT models using ElevenLabs TTS. 

Input currently only takes in text, but ElevenLabs is used to produce a natural sounding voice.

API access for both are required.

# Installing 

1. Assuming you have python installed, all you need to do is

        pip install -r requirements.txt

# Use

To use this bot, run it with

    python voice_chat.py --openai_key <openapi_key> --elevenlabs_key <elevenlabs_key>

or copy `.template.env` and rename it `.env`, and fill in the keys there instead. Now it can be run as 

    python voice_chat.py

Additional settings can be modified either via passing in the parameter as an arguement, or by modifying `config.json` (Recommended), which is created after the first run.

Help and settings can be found by running

    python voice_chat.py -h

# Features

- Can provide a default context to the bot
- Can name the bot, and adjust various parameters