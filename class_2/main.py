import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel,RunConfig,Runner,function_tool
from pydantic import config
import json


# Load .env file
load_dotenv()

# Get API key from environment
gemini_api_key = os.getenv("gemini_API_KEY")


if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
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






@function_tool
def list_todos():
    """List all todos from the todos.json file."""
    try:
        print("Listing todos...")
        with open(r"D:\ApenAi\class_2\todos.json", "r") as file:
            data = json.load(file)
        return data.get(  "todos", [])
    except Exception as e:
        print(f"Error: {e}")
        raise FileNotFoundError("The file todos.json was not found.")






@function_tool
def add_todo(todo: str):
    """Add a new todo to the todos.json file."""
    try:
        print("Adding todo...")
        with open(r"D:\ApenAi\class_2\todos.json", "r") as file:
            data = json.load(file)
        if "todos" not in data:
            data["todos"] = []
        data["todos"].append(todo)
        with open(r"D:\ApenAi\class_2\todos.json", "w") as file:
            json.dump(data, file)
        return f"Added {todo} to the list."
    except Exception as e:
        print(f"Error: {e}")
        raise FileNotFoundError("The file todos.json was not found.")





@function_tool
def delete_todo(index: int):
    """Delete a todo from the todos.json file by its index."""
    try:
        print("Deleting todo...")
        with open(r"D:\ApenAi\class_2\todos.json", "r") as file:
            data = json.load(file)
        todos = data.get("todos", [])
        if 0 <= index < len(todos):
            deleted_todo = todos.pop(index)
            data["todos"] = todos
            with open(r"D:\ApenAi\class_2\todos.json", "w") as file:
                json.dump(data, file)
            return f"Deleted {deleted_todo} from the list."
        else:
            return "Invalid index. Please provide a valid index."
    except Exception as e:
        print(f"Error: {e}")
        raise FileNotFoundError("The file todos.json was not found.")








@function_tool
def update_todo(index: int, new_content: str):
    """Update a todo in the todos.json file by its index with new content."""
    try:
        print("Updating todo...")
        with open(r"D:\ApenAi\class_2\todos.json", "r") as file:
            data = json.load(file)
        todos = data.get("todos", [])
        if 0 <= index < len(todos):
            todos[index] = new_content
            data["todos"] = todos
            with open(r"D:\ApenAi\class_2\todos.json", "w") as file:
                json.dump(data, file)
            return f"Updated todo at index {index} with {new_content}."
        else:
            return "Invalid index. Please provide a valid index."
    except Exception as e:
        print(f"Error: {e}")
        raise FileNotFoundError("The file todos.json was not found.")






agent = Agent(
    name="Agent",
    instructions="""

    Fist of You say Sir, You are Name Haroon Rasheed
You are a smart and helpful assistant that manages a Todo List .
1. If the user asks you to add a new item to the todo list, add it to the list and confirm the addition.
2. If the user asks you to delete an item from the todo list, delete it and confirm the deletion.
3. If the user asks you to show the todo list, display all current todo items or say it is empty.
4. If the user asks you to update an existing todo item, update it and confirm the update.
5. If the user asks any other question, answer the question politely.

1. Add new items to the todo list when requested.
2. Delete existing items from the todo list based on the user's instructions.
3. Show the current todo list when the user asks.
4. Update existing todo list items with new content.



""",
tools=[
    list_todos,
    add_todo,
    delete_todo,
    update_todo
]

)


def main():
    """Main interaction loop for the todo list assistant."""
    print("Welcome, Sir Haroon Rasheed! I'm your todo list assistant.")

    while True:
        say = input("What do you want to say? (or 'quit' to exit): ").strip()



        if say.lower() == "quit":
            print("Goodbye, Sir!")
            break
        try:
            response = Runner.run_sync(
                agent,
                input=say,
                run_config=config
            )
            print(response.final_output)
        except Exception as e:
            print(f"Agent error: {str(e)}. Please check your Gemini API key or network connection.")

if __name__ == "__main__":
    main()







