from agents import Agent, Runner
import my_config


agent = Agent (
    name="Haroon Rasheed web Agent",
    instructions="You are a helpful assistant that answers questions about web development. First, you say 'Sir' and then you answer the question. Your name is Haroon Rasheed."
   
)


res = Runner.run_sync(
    agent,
    input="what is name ?",
    run_config=my_config.config,
    
)

print(res.final_output)
