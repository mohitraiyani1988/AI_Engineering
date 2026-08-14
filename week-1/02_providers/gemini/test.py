import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

start = time.perf_counter()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain what an API is to a junior software developer in exactly 3 paragraphs. Include one practical example."
)

elapsed = time.perf_counter() - start

usage = response.usage_metadata

print("\nResponse:")
print(response.text)

print("\nModel:", response.model_version)

print("\nInput tokens:", usage.prompt_token_count)

print("\nOutput tokens:", usage.candidates_token_count)

print("\nThought tokens:", usage.thoughts_token_count)

print("\nTotal tokens:", usage.total_token_count)

print("\nFinish reason:",response.candidates[0].finish_reason)

print(f"Time:           {elapsed:.2f}s")