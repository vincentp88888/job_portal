from modules.gemini_llm import GeminiLLM
import os

# Set API key
api_key = input("Enter your Gemini API key: ")
os.environ['GEMINI_API_KEY'] = api_key

# Test
llm = GeminiLLM(model_name="gemini-1.5-flash")

prompt = "Write a short professional summary for an IT Project Manager with 10 years experience."

print("\nGenerating...")
response = llm.generate(prompt)
print("\nResponse:")
print(response)
print("\n✅ Test successful!")
