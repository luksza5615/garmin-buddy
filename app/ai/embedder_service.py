import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") 

client = genai.Client(api_key=api_key)

result = client.models.embed_content(
    model='gemini-embedding-001',
    contents='Content to be embedded'
)

print(result.embeddings)

