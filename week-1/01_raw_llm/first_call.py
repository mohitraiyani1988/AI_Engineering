import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain what is API in short."
)


usage = response.usage_metadata

print("\nResponse:")
print(response.text)

print("\nModel:")
print(response.model_version)

print("\nInput tokens:")
print(usage.prompt_token_count)

print("\nOutput tokens:")
print(usage.candidates_token_count)

print("\nThought tokens:")
print(usage.thoughts_token_count)

print("\nTotal tokens:")
print(usage.total_token_count)

print("\nFinish reason:")
print(response.candidates[0].finish_reason)