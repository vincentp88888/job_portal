from modules.gemini_llm import GeminiLLM

print("=" * 70)
print("TESTING 2025 GEMINI MODELS")
print("=" * 70)

api_key = input("\nEnter your Gemini API key: ")

# Test recommended models
models_to_test = [
    "gemini-2.5-flash",      # Recommended
    "gemini-flash-latest",   # Latest
    "gemini-2.5-pro",        # Best quality
]

for model_name in models_to_test:
    print(f"\n{'=' * 70}")
    print(f"Testing: {model_name}")
    print('=' * 70)
    
    try:
        llm = GeminiLLM(api_key=api_key, model_name=model_name)
        response = llm.generate("Say hello in one short sentence", max_tokens=50)
        
        print(f"✅ SUCCESS!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nRecommended model: gemini-2.5-flash")
