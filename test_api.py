import openai
import os
from dotenv import load_dotenv

load_dotenv()

def test_openai_connection():
    print("Testing OpenAI API connection...")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    print(f"✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Set API key
    openai.api_key = api_key
    
    # Test connection
    try:
        print("\nTesting API call...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=10
        )
        
        print("✅ SUCCESS! API is working")
        print(f"Response: {response.choices.message.content}")
        return True
        
    except openai.AuthenticationError:
        print("❌ AUTHENTICATION ERROR: Invalid API key")
        return False
        
    except openai.APIConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("\nPossible causes:")
        print("1. Firewall blocking OpenAI")
        print("2. No internet connection")
        print("3. Corporate proxy required")
        print("4. VPN needed")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection()
