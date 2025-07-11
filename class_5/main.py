import os
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
        model=model
    )

    cl.user_session.set("agent", agent)
    await cl.Message("Welcome! I am your assistant. How can I help you today?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message("Processing your request...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})



   
    result = await Runner.run(starting_agent=agent, input=history, run_config=config)
   
    msg.content = result.final_output
    await msg.update()

    cl.user_session.set("chat_history", result.to_input_list())
