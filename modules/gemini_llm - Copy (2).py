<<<<<<< HEAD
import google.generativeai as genai
import os
import ssl
import certifi
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    """Google Gemini API wrapper with SSL fix"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """Initialize Gemini with SSL workaround"""
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Gemini API key required")
        
        # FIX 1: Disable SSL verification (quick fix for corporate networks)
        # This allows connections through corporate proxies
        os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'
        os.environ['GRPC_POLL_STRATEGY'] = 'poll'
        
        # Configure Gemini
        genai.configure(
            api_key=self.api_key,
            transport='rest'  # Use REST instead of gRPC to avoid SSL issues
        )
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        print(f"✅ Gemini {self.model_name} initialized with REST transport")
    
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
            
            if "quota" in error_msg.lower():
                return "⚠️ Quota exceeded. Please wait a moment."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters."
            else:
                return f"Error: {error_msg}"
    
    # ... rest of methods stay the same
=======
import google.generativeai as genai
import os
import ssl
import certifi
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    """Google Gemini API wrapper with SSL fix"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """Initialize Gemini with SSL workaround"""
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Gemini API key required")
        
        # FIX 1: Disable SSL verification (quick fix for corporate networks)
        # This allows connections through corporate proxies
        os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'
        os.environ['GRPC_POLL_STRATEGY'] = 'poll'
        
        # Configure Gemini
        genai.configure(
            api_key=self.api_key,
            transport='rest'  # Use REST instead of gRPC to avoid SSL issues
        )
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        print(f"✅ Gemini {self.model_name} initialized with REST transport")
    
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
            
            if "quota" in error_msg.lower():
                return "⚠️ Quota exceeded. Please wait a moment."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters."
            else:
                return f"Error: {error_msg}"
    
    # ... rest of methods stay the same
>>>>>>> 1567d1cc7060c3393434b99c0f195ebd24a1f3c1
