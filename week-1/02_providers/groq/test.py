import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

PROMPT = """
Explain what an API is to a junior software developer in exactly 3 paragraphs. Include one practical example.
"""

start = time.perf_counter()

response = client.chat.completions.create(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    messages=[
        {
            "role": "user",
            "content": PROMPT
        }
    ]
)

elapsed = time.perf_counter() - start

message = response.choices[0].message
usage = response.usage

print("=" * 60)

print("\nResponse:")
print(message.content)

print("\n--- Metadata ---")

print(f"Model:          {response.model}")
print(f"Input tokens:   {usage.prompt_tokens}")
print(f"Output tokens:  {usage.completion_tokens}")
print(f"Total tokens:   {usage.total_tokens}")
print(f"Time:           {elapsed:.2f}s")

print(f"\nFinish reason:  {response.choices[0].finish_reason}")
