import os
import json
from typing import cast
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
from chainlit.element import Image

# ==== Load Env ====
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

# ==== Paths ====
PRODUCT_FILE_PATH = r"C:\Users\hp\Desktop\uv\New folder (2)\project\products.json"
ORDER_FILE_PATH = r"C:\Users\hp\Desktop\uv\New folder (2)\project\orders.json"

# ==== Chat Start ====
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

    config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    agent = Agent(
        name="Assistant",
        instructions="""
Hello Sir! I am your assistant Haroon Rasheed. My job is to help you manage your products.

🛠️ Here’s what I can help you with:

1. ✅ Add a product — (name, description, image_url, price).
2. 🗑️ Delete a product — by name.
3. 📋 List all products — with numbering and images.
4. ✏️ Update a product — by name.
5. 🛍️ When you say "kharidna hai" (I want to buy), I will:
    - Ask for customer name, address, and phone number.
    - 📞 If the phone number is invalid (too short or doesn't look like a phone number), I will politely ask the user to correct it.
    - 🚫 If any field is missing, I will request the complete information before placing the order.

6. ✅ Once all info is valid:
    - I will mark the product as `purchased = true`.
    - Save the order in `orders.json`.

7. ☎️ After each order, I will show Haroon Rasheed’s contact number: **03412231142** for follow-up.

8. 🔍 If user says "filter Chair" or any keyword, I will only show matching products with images and details.

⚠️ I will always reply in Roman Urdu or English — based on user’s input language.  
""",
        model=model,
        tools=[
            list_products,
            add_product,
            delete_product,
            update_product,
            purchase_product_with_user,
            filter_products_by_keyword  # Naya tool add kiya hai filter ke liye
        ]
    )

    cl.user_session.set("agent", agent)
    await cl.Message(content="🛒 Welcome Sir! Product Assistant ready.").send()

# ==== Tools ====

@function_tool
async def list_products():
    """List all products with details and show images."""
    try:
        if not os.path.exists(PRODUCT_FILE_PATH):
            return "Product list is empty."

        with open(PRODUCT_FILE_PATH, "r") as file:
            data = json.load(file)

        products = data.get("products", [])
        if not products:
            return "Product list is empty."

        for i, p in enumerate(products, start=1):
            status = "✅ Purchased" if p.get("purchased") else "🛒 Available"
            await cl.Message(
                
                
                content=(
                    f"**{i}. {p['name']}**\n"
                    f"![Image]({p['image_url']})\n"
                    f"📝 {p['description']}\n"
                    f"💰 Rs. {p['price']}\n"
                    f"{status}"
                )
                
            ).send()

        return "✅ All products listed with images."
    except Exception as e:
        return f"Error: {e}"

@function_tool
def add_product(name: str, description: str, image_url: str, price: float):
    try:
        data = {"products": []}
        if os.path.exists(PRODUCT_FILE_PATH):
            with open(PRODUCT_FILE_PATH, "r") as file:
                data = json.load(file)

        data["products"].append({
            "name": name,
            "description": description,
            "image_url": image_url,
            "price": price,
            "purchased": False
        })

        with open(PRODUCT_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

        return f"✅ Product '{name}' added successfully."
    except Exception as e:
        return f"Error: {e}"

@function_tool
def delete_product(index: int):
    try:
        if not os.path.exists(PRODUCT_FILE_PATH):
            return "Product list is empty."

        with open(PRODUCT_FILE_PATH, "r") as file:
            data = json.load(file)

        products = data.get("products", [])
        if 0 <= index < len(products):
            removed = products.pop(index)
            with open(PRODUCT_FILE_PATH, "w") as file:
                json.dump({"products": products}, file, indent=4)
            return f"🗑️ Deleted product: {removed['name']}"
        else:
            return "❌ Invalid index."
    except Exception as e:
        return f"Error: {e}"

@function_tool
def update_product(index: int, name: str, description: str, image_url: str, price: float):
    try:
        if not os.path.exists(PRODUCT_FILE_PATH):
            return "Product list is empty."

        with open(PRODUCT_FILE_PATH, "r") as file:
            data = json.load(file)

        products = data.get("products", [])
        if 0 <= index < len(products):
            products[index] = {
                "name": name,
                "description": description,
                "image_url": image_url,
                "price": price,
                "purchased": products[index].get("purchased", False)
            }
            with open(PRODUCT_FILE_PATH, "w") as file:
                json.dump({"products": products}, file, indent=4)
            return f"✏️ Product at index {index} updated."
        else:
            return "❌ Invalid index."
    except Exception as e:
        return f"Error: {e}"

@function_tool
def purchase_product_with_user(index: int, user_name: str, user_address: str, user_contact: str):
    try:
        if not os.path.exists(PRODUCT_FILE_PATH):
            return "Product list is empty."

        with open(PRODUCT_FILE_PATH, "r") as file:
            data = json.load(file)

        products = data.get("products", [])
        if not (0 <= index < len(products)):
            return "❌ Invalid index."

        product = products[index]
        product["purchased"] = True

        with open(PRODUCT_FILE_PATH, "w") as file:
            json.dump({"products": products}, file, indent=4)

        order = {
            "product_name": product["name"],
            "price": product["price"],
            "user_name": user_name,
            "user_address": user_address,
            "user_contact": user_contact,
            "seller_name": "Haroon Rasheed",
            "seller_contact": "03412231142"
        }

        orders = []
        if os.path.exists(ORDER_FILE_PATH):
            with open(ORDER_FILE_PATH, "r") as file:
                orders = json.load(file)

        orders.append(order)

        with open(ORDER_FILE_PATH, "w") as file:
            json.dump(orders, file, indent=4)

        return (
            f"🛍️ Order placed!\n"
            f"📦 Product: {product['name']}\n"
            f"💰 Price: Rs. {product['price']}\n"
            f"👤 Name: {user_name}\n"
            f"🏠 Address: {user_address}\n"
            f"📞 Contact Haroon Rasheed: 03412231142"
        )
    except Exception as e:
        return f"Error: {e}"

# ==== New: Filter Products By Keyword ====

@function_tool
async def filter_products_by_keyword(keyword: str):
    try:
        if not os.path.exists(PRODUCT_FILE_PATH):
            return "Product list is empty."

        with open(PRODUCT_FILE_PATH, "r") as file:
            data = json.load(file)

        products = data.get("products", [])
        filtered = [p for p in products if keyword.lower() in p['name'].lower() or keyword.lower() in p['description'].lower()]
        if not filtered:
            return f"No products found with keyword '{keyword}'."

        for i, p in enumerate(filtered, start=1):
            status = "✅ Purchased" if p.get("purchased") else "🛒 Available"
            await cl.Message(
                content=(
                    f"**{i}. {p['name']}**\n"
                    f"📝 {p['description']}\n"
                    f"💰 Rs. {p['price']}\n"
                    f"{status}"
                ),
                elements=[
                    Image(name=p['name'], display="inline", url=p['image_url'])
                ]
            ).send()

        return f"✅ Filtered products with keyword '{keyword}' listed."
    except Exception as e:
        return f"Error: {e}"

# ==== Message Handler ====

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="⏳ Thinking...")
    await msg.send()

    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    history = cl.user_session.get("chat_history") or []

    user_msg = message.content.strip().lower()

    # Keyword based routing for filter
    if user_msg.startswith("filter "):
        keyword = user_msg.split("filter ",1)[1].strip()
        result = await filter_products_by_keyword(keyword)
        await msg.update(content=result)
        return

    history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_sync(starting_agent=agent, input=history, run_config=config)
        msg.content = result.final_output
        await msg.update()
        cl.user_session.set("chat_history", result.to_input_list())
    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
