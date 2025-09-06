import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

instructions = """
                you are a helpful assistant, you help the user while he is using his laptop. 
                you get a text which is a transcription of a recording of something that the user said while he is using his laptop.
                you analyze a what the user said and decide if this text is the user asking the LLM a question.
                you also analyze if the question is about something that the user is looking at on the screen.
                you should decide if a screenshot is needed to help you answer the user's question.
                if a screenshot is need use the appropriate tool
                """

def analyze_text(text: str) -> bool:

    # Classify
    res = client.chat.completions.parse(
        model="gpt-4.1-mini",
        response_format=UserVoiceAnalysis,
        messages=[
            {
                "role": "system", 
                "content": instructions
            },
            {
                "role": "user", 
                "content": text
            }
        ],
    )
    out = res.choices[0].message.content
    analysis_response = UserVoiceAnalysis.model_validate_json(out)
    return analysis_response

if __name__ == "__main__":
    res = analyze_text('איזה אפליקציות פתוחות לי על המחשב כרגע')
    print(res)