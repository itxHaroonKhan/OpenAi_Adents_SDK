from agents import Agent, Runner, function_tool, RunContextWrapper
import my_config
from pydantic import BaseModel



class UserInfo(BaseModel):
    Name: str
    age: int
    Rool_No: str
    
    
    
    


def dynamic_instructions(context: RunContextWrapper[UserInfo], agent: Agent[UserInfo]) -> str:
    return f"The user's name is {context.context.Name}. Help them with their questions."


@function_tool
def get_age(ctx: RunContextWrapper[UserInfo]):
    """Get user's age by age"""
    
    return f" age is {ctx.context.age}"




obj = UserInfo(
        Name="Haroon Rasheed",
        age=18,
        Rool_No="123"
    )




agent = Agent[UserInfo](
    name="Helpful Assistant",
    instructions=dynamic_instructions,
    tools=[get_age]
)




res = Runner.run_sync(
    agent,
    input="what is user age?",
    run_config=my_config.config,
    context=obj
)


print(res.final_output)
