import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from playsound import playsound

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def talk(text):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as resp:
        # save to a temp MP3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp_path = f.name
        resp.stream_to_file(tmp_path)

    print('before play sound')
    playsound(tmp_path)   # plays the MP3
    print('after play sound')
    os.remove(tmp_path)   # clean up
