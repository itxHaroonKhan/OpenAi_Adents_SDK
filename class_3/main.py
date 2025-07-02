
import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, RunConfig, Runner, OpenAIChatCompletionsModel
import asyncio


load_dotenv()


API = os.getenv("API_KEY")


client = AsyncOpenAI(api_key=API,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
     openai_client=client
)


config = RunConfig(model=model, model_provider=client, tracing_disabled=True)



async def main():
    print("Welcome, Sir Haroon Rasheed!")

    agent = Agent(
        name="Gemini Agent",
        instructions="Your name is Haroon and you are a helpful assistant."
    )

    while True:
        say = input("How can I help you? ")

        # Exit condition
        if say.lower() in ["exit", "quit", "bye"]:
            print("Goodbye, Sir Haroon!")
            break

        response = await Runner.run(
            agent,
            input=say,
            run_config=config
        )

        print("\nAssistant:", response.final_output, "\n")


asyncio.run(main())