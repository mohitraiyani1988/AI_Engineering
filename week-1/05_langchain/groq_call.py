import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    groq_api_key=os.getenv("GROQ_API_KEY")
)

response = llm.invoke(
    "Explain what an API is in one paragraph."
)

print(response)
