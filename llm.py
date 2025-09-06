import queue, time, threading, signal, sys, os, base64
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import ImageGrab

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

instructions = """
                you are a helpful assistant, you help the user while he is using his laptop. 
                you get a text which is a transcription of a recording of something that the user said while he is using his laptop.
                you analyze what the user said and you decide if this text is the user asking the LLM a question.
                you also analyze if the question is about something that the user is looking at on the screen or not.
                you should decide if a screenshot is needed to help you answer the user's question.
                if a screenshot is need use the appropriate tool

                keep your answers very short and to the point. 
                do not elaborate, be consice.
                Answer only on the specific question your asked about.
                do not give details beyond what you are specifically asked about.
                Always answer with the shortest possible response.
                Do not explain things unless you are explicitly asked about.
                do not suggest any farther help. 
                do not ask the user questions.                
               """

llm = ChatOpenAI(
    api_key=api_key, 
    model_kwargs={
        "messages": [{
                "role": "system", 
                "content": instructions
        }]
    }
)


@tool
def take_screenshot_and_convert_to_base64() -> str:
    """Capture a screenshot of the current screen and return it as base64."""
    ImageGrab.grab(all_screens=True).save('screenshot.png')

    print('encode the file to base64: ', datetime.now().strftime("%H:%M:%S"))
    with open('screenshot.png', "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    return img_base64

@tool
def get_weather(city):
    """return the weather in the provided city"""
    return f"the weather in {city} is sunny!"

def llm_response(text):

    # Classify
    agent = initialize_agent(
        llm=llm,
        tools=[take_screenshot_and_convert_to_base64],
        agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
    )
    out = agent.invoke(text)
    return out


if __name__ == "__main__":
    # res = llm_response('איזה אפליקציות פתוחות לי על המחשב כרגע')
    res = llm_response(input('what is your questions? '))
    print(res)