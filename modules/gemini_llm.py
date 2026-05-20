import google.generativeai as genai
import os
import certifi
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    """Google Gemini API wrapper with 2025 model names"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini with correct 2025 model names
        
        Valid models (from your API):
        - gemini-2.5-flash (RECOMMENDED - stable, fast, 1M tokens)
        - gemini-2.5-pro (best quality)
        - gemini-flash-latest (always latest flash)
        - gemini-pro-latest (always latest pro)
        - gemini-2.0-flash (older but stable)
        
        Args:
            api_key: Gemini API key
            model_name: Model to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )
        
        # SSL Fix
        try:
            cert_path = certifi.where()
            os.environ['SSL_CERT_FILE'] = cert_path
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            print(f"✅ Using certificates: {cert_path}")
        except:
            pass
        
        # Configure API with REST transport
        genai.configure(
            api_key=self.api_key,
            transport='rest'
        )
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        print(f"✅ Gemini initialized: {self.model_name}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """Generate text using Gemini"""
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        config = self.generation_config.copy()
        config['temperature'] = temperature
        config['max_output_tokens'] = max_tokens
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "⚠️ Rate limit exceeded. Wait 60 seconds and try again."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Try rephrasing."
            elif "404" in error_msg or "not found" in error_msg.lower():
                return (
                    f"⚠️ Model '{self.model_name}' not found.\n"
                    "Valid models: gemini-2.5-flash, gemini-2.5-pro, gemini-flash-latest"
                )
            else:
                return f"Error: {error_msg}"
    
    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7):
        """Stream response for real-time display"""
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        config = self.generation_config.copy()
        config['temperature'] = temperature
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            yield f"Error: {e}"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Multi-turn conversation"""
        
        chat = self.model.start_chat(history=[])
        
        for msg in messages:
            if msg['role'] == 'user':
                response = chat.send_message(msg['content'])
        
        return response.text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except:
            return len(text) // 4
