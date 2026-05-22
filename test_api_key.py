import google.generativeai as genai
import os

# Get API key
api_key = input("Enter your Gemini API key: ")

print("\n" + "=" * 70)
print("TESTING API KEY")
print("=" * 70)

try:
    # Configure with API key
    genai.configure(api_key=api_key)
    print("✅ API key format is valid")
    print("✅ Successfully configured")
except Exception as e:
    print(f"❌ Error configuring API: {e}")
    exit(1)
