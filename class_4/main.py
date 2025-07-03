

import os 
from dotenv import load_dotenv
from litellm import completion



load_dotenv()

def main():

    api_key = os.getenv("API_KEY")
    
     

    response = completion(
     api_key=api_key,
     model="gemini/gemini-2.0-flash",
     messages=[
         {
          "role": "user",
          "content": "Hello, how are you?"
          }
         ]
)

    print(response['choices'][0]['message']['content'])



if __name__ == "__main__":
    main()