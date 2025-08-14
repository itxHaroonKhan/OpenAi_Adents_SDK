
import os
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig


load_dotenv()
API = os.getenv('GROQ_API_KEY')


client = AsyncOpenAI(
    api_key=API,
     base_url="https://api.groq.com/openai/v1",
)


model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client
)


config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)
