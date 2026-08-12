import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PROMPT = """
Write a short story in exactly 5 sentences about
a developer who discovers a mysterious sensor.
"""

start = time.perf_counter()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        max_output_tokens=50
    )
)

elapsed = time.perf_counter() - start

usage = response.usage_metadata

print("=" * 60)

print("\nResponse:")
print(response.text)

print("\n--- Metadata ---")

print(f"Model:          {response.model_version}")
print(f"Input tokens:   {usage.prompt_token_count}")
print(f"Output tokens:  {usage.candidates_token_count}")
print(f"Thought tokens: {usage.thoughts_token_count}")
print(f"Total tokens:   {usage.total_token_count}")
print(f"Time:           {elapsed:.2f}s")

print(f"\nFinish reason:  {response.candidates[0].finish_reason}")