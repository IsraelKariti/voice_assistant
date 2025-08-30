import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

instructions = """
                you are a helpful assistant, you help the user while he is using his laptop. 
                keep your answers short and to the point. do not elaborate. do not suggest any farther help. 
                do not ask the user questions.
               """

def llm_response(text, img_base64):

    # Classify
    res = client.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system", 
                "content": instructions
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        },
                    },
                ]
            }
        ],
    )
    out = res.choices[0].message.content
    return out

if __name__ == "__main__":
    res = analyze_text('איזה אפליקציות פתוחות לי על המחשב כרגע')
    print(res)