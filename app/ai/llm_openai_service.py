from openai import OpenAI 
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=key)

def generate_response():
    response = client.responses.create(
        model ="gpt-4.1-mini",
        input = [
            {"role" : "system", "content": "You're experienced running coach"},
            {"role": "user", "content": "Explain me what intervals are"}
        ]
    )
    print(response)

    return response 

if __name__ == "__main__":
    generate_response()