from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

print(f"API key loaded: {api_key[:8]}...")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

print("Connecting to Gemini...")

response = llm.invoke("Say exactly this and nothing else: DealSense on Gemini is ready.")

print("\n--- Response ---")
print(response.content)
print("----------------")
print("\n✓ Connection successful. Proceed to Day 1 vibe coding prompt.")
