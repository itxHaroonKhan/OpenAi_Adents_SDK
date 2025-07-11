import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
import json

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

STUDENT_FILE_PATH = r"C:\Users\hp\Desktop\uv\New folder (2)\project\students.json"

@cl.on_chat_start
async def start():
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

    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    agent: Agent = Agent(
        name="Assistant",
        instructions="""
First say "Sir". Your name is Haroon Rasheed.
You are a helpful assistant that manages a Student List.

⚠️ Important Rule:
Always reply in the **same language** the user used (Roman Urdu or English).

Student Manager Rules:
1. Add student with name, roll number, and address.
2. Delete a student by index.
3. Show all students with numbering and details.
4. Update a student record by index.
5. Answer politely in the same language as the question.
""",
        model=model,
        tools=[
            list_students,
            add_student,
            delete_student,
            update_student
        ]
    )

    cl.user_session.set("agent", agent)
    await cl.Message(content="Welcome Sir! Student List Assistant ready.").send()

# ==== FUNCTION TOOLS ====

@function_tool
def list_students():
    """List all students with details."""
    try:
        if not os.path.exists(STUDENT_FILE_PATH):
            return "Student list is empty."
        with open(STUDENT_FILE_PATH, "r") as file:
            data = json.load(file)
        students = data.get("students", [])
        if not students:
            return "Student list is empty."
        formatted = ""
        for i, s in enumerate(students, start=1):
            formatted += f"{i}. Name: {s['name']}, Roll No: {s['roll_no']}, Address: {s['address']}\n"
        return formatted.strip()
    except Exception as e:
        print(f"Error in list_students: {e}")
        return "Error loading student list."

@function_tool
def add_student(name: str, roll_no: str, address: str):
    """Add a student with name, roll_no, and address."""

    try:
        
        data = {"students": []}
        if os.path.exists(STUDENT_FILE_PATH):
            with open(STUDENT_FILE_PATH, "r") as file:
                data = json.load(file)
        data["students"].append({
            "name": name,
            "roll_no": roll_no,
            "address": address
        })
        with open(STUDENT_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        return f"Student '{name}' added successfully."
    except Exception as e:
        print(f"Error in add_student: {e}")
        return "Error adding student."

@function_tool
def delete_student(index: int):
    """Delete a student by index."""
    try:
        if not os.path.exists(STUDENT_FILE_PATH):
            return "Student list is empty."
        with open(STUDENT_FILE_PATH, "r") as file:
            data = json.load(file)
        students = data.get("students", [])
        if 0 <= index < len(students):
            removed = students.pop(index)
            data["students"] = students
            with open(STUDENT_FILE_PATH, "w") as file:
                json.dump(data, file, indent=4)
            return f"Deleted student '{removed['name']}' successfully."
        else:
            return "Invalid index."
    except Exception as e:
        print(f"Error in delete_student: {e}")
        return "Error deleting student."

@function_tool
def update_student(index: int, name: str, roll_no: str, address: str):
    """Update a student record by index."""
    try:
        if not os.path.exists(STUDENT_FILE_PATH):
            return "Student list is empty."
        with open(STUDENT_FILE_PATH, "r") as file:
            data = json.load(file)
        students = data.get("students", [])
        if 0 <= index < len(students):
            students[index] = {"name": name, "roll_no": roll_no, "address": address}
            data["students"] = students
            with open(STUDENT_FILE_PATH, "w") as file:
                json.dump(data, file, indent=4)
            return f"Updated student at index {index}."
        else:
            return "Invalid index."
    except Exception as e:
        print(f"Error in update_student: {e}")
        return "Error updating student."

# ==== CHAT MESSAGE HANDLER ====

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()

    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    history = cl.user_session.get("chat_history") or []
    history.append({
        "role": "user",
        "content": message.content
    })

    try:
        result = Runner.run_sync(starting_agent=agent, input=history, run_config=config)
        msg.content = result.final_output
        await msg.update()
        cl.user_session.set("chat_history", result.to_input_list())
    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
