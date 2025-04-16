# backend/clients/gemini_client.py
import os
import httpx
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

class GeminiClient:
    """Client for interacting with the Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini API client.
        
        Args:
            api_key: Gemini API key, defaults to GEMINI_API_KEY env variable
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.generation_model = "gemini-pro"
        self.embedding_model = "models/embedding-001"
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: The text prompt to send to Gemini
            
        Returns:
            The generated text response
            
        Raises:
            HTTPException: If the API call fails
        """
        url = f"{self.base_url}/models/{self.generation_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        
        # Prepare request body
        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, params=params, json=body, timeout=30)
                
                # Handle non-200 responses
                if response.status_code != 200:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown API error")
                    raise HTTPException(status_code=response.status_code, detail=error_message)
                
                # Extract and return the generated text
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request to Gemini API timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Error communicating with Gemini API: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List of embedding values
            
        Raises:
            HTTPException: If the API call fails
        """
        url = f"{self.base_url}/{self.embedding_model}:embedContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        
        # Prepare request body
        body = {
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, params=params, json=body, timeout=10)
                
                # Handle non-200 responses
                if response.status_code != 200:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown API error")
                    raise HTTPException(status_code=response.status_code, detail=error_message)
                
                # Extract and return embeddings
                result = response.json()
                return result.get("embedding", {}).get("values", [])
                
        except Exception as e:
            # For production, consider returning an empty list instead of raising an exception
            # to prevent embeddings issues from breaking the core functionality
            print(f"Embedding generation error: {str(e)}")
            return []