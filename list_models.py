import google.generativeai as genai

# Enter your API key
api_key = input("Enter your Gemini API key: ")

print("\n" + "=" * 70)
print("LISTING AVAILABLE GEMINI MODELS")
print("=" * 70 + "\n")

try:
    # Configure API
    genai.configure(api_key=api_key)
    
    # List all models
    models = genai.list_models()
    
    print("Available models that support 'generateContent':\n")
    
    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ Model: {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Supported Methods: {model.supported_generation_methods}")
            print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. API key doesn't have required permissions")
    print("3. Network/firewall blocking Google API")
