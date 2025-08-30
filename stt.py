import os 
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def convert_speech_to_text(wav_file):
    with open(wav_file, "rb") as f:
        tx = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",  # or "whisper-1"
            file=f
        )
    text = tx.text
    return text

if __name__ == "__main__":
    convert_speech_to_text('1capture.wav')