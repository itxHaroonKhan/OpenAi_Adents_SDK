import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel,RunConfig,Runner





load_dotenv()


gemini_api_key = os.getenv("gemini_API_KEY")




external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
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




agent = Agent(
    name="Haroon Rasheed web Agent",
    instructions="You are a helpful assistant that answers questions about web development. Fist,You say 'Sir' and then you answer the question You are Name Haroon Rasheed",

)



say = input("Enter You Are Question ? : ")

response = Runner.run_sync(
    agent,
    input= say,
    run_config=config
)


print(response.final_output)
