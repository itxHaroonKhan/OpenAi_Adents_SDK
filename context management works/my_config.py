
import os
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig


load_dotenv()
API = os.getenv('API_GOOGLE')


client = AsyncOpenAI(
    api_key=API,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client
)


config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)
