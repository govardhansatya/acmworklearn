# main.py - Integrated FastAPI Application

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import motor.motor_asyncio
import httpx
import uuid
import jwt
import json
import requests
from dotenv import load_dotenv

# Import generator modules
from backend.generators.poetry_generator import generate_poetry
from backend.generators.melody_generator import generate_melody
from backend.generators.game_script_generator import generate_game_script
from backend.utils.utils import detect_extend_intent, build_prompt, generate_text_gemini, embed_text_gemini
from backend.utils.mongo import save_creative_output, get_session_history, save_user_feedback

# Load env variables
load_dotenv()

# --- Auth Configuration ---
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ['RS256']  # JWT algorithm

# --- Init ---
app = FastAPI(title="Creative Buddy API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# MongoDB Connection
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME", "creative_buddy")]

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Auth Security ---
security = HTTPBearer()

# --- Models ---
class GenerateRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    input_text: str
    type: str  # poetry | melody | script

class FeedbackRequest(BaseModel):
    user_id: str
    output_id: str
    feedback: str
    rating: Optional[int] = None

class HistoryRequest(BaseModel):
    user_id: str
    session_id: str

# --- Auth Helper Functions ---
def get_jwks():
    """Fetch the JSON Web Key Set from Auth0"""
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(url)
    return response.json()

def verify_jwt(token: str) -> Dict[str, Any]:
    """Verify JWT token and return decoded payload if valid"""
    try:
        # Get the public key
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the matching key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Verify the token
        payload = jwt.decode(
            token,
            jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid claims, check audience and issuer")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

# Auth dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate the token and return user info"""
    token = credentials.credentials
    payload = verify_jwt(token)
    return payload

# --- Routes ---
@app.get("/")
async def root():
    """Root endpoint that returns API info"""
    return {
        "message": "Welcome to Creative Buddy API!", 
        "version": "1.0.0",
        "endpoints": [
            {"path": "/generate", "method": "POST", "description": "Generate creative content"},
            {"path": "/feedback", "method": "POST", "description": "Provide feedback on generated content"},
            {"path": "/history", "method": "POST", "description": "Get session history"}
        ]
    }

@app.post("/generate")
async def generate_creative(request: GenerateRequest, user: Dict = Depends(get_current_user)):
    """Generate creative content based on user input"""
    
    # Validate that the requesting user matches the user_id in the request
    if user.get("sub") != request.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Get context from previous interactions if this is an extension
    previous_output = None
    
    if request.session_id:
        # Get the most recent history item for this session
        history = await get_session_history(request.session_id, limit=1)
        if history and detect_extend_intent(request.input_text):
            previous_output = history[0].get("output", "")
    
    try:
        # Use the appropriate generator based on content type
        if request.type == "poetry":
            result = await generate_poetry(
                db, 
                request.user_id, 
                request.input_text, 
                request.session_id, 
                previous_output, 
                generate_text_gemini
            )
        elif request.type == "melody":
            result = await generate_melody(
                db, 
                request.user_id, 
                request.input_text, 
                request.session_id, 
                previous_output, 
                generate_text_gemini
            )
        elif request.type == "script":
            result = await generate_game_script(
                db, 
                request.user_id, 
                request.input_text, 
                request.session_id, 
                previous_output, 
                generate_text_gemini
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {request.type}")
        
        # Get the output from the result
        output = result.get("output", "")
        
        # Generate embedding for semantic search
        embedding = await embed_text_gemini(output)
        
        # Save to database with common fields and any additional metadata
        metadata = {k: v for k, v in result.items() if k not in ["output", "type", "mode"]}
        save_result = await save_creative_output(
            request.user_id,
            request.input_text,
            output,
            request.type,
            request.session_id,
            result.get("mode", "new"),
            metadata,
            embedding
        )
        
        # Return the result with session information
        return {
            "output": output,
            "session_id": save_result["session_id"],
            "output_id": save_result["output_id"],
            "mode": result.get("mode", "new"),
            **metadata  # Include any specialized metadata from the generators
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@app.post("/feedback")
async def provide_feedback(
    request: FeedbackRequest, 
    user: Dict = Depends(get_current_user)
):
    """Store user feedback for a generated output"""
    
    # Validate the user
    if user.get("sub") != request.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    try:
        # Save the feedback
        result = await save_user_feedback(
            request.user_id,
            request.output_id,
            request.feedback,
            request.rating
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Output not found")
        
        return {"message": "Feedback received", "status": "success"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

@app.post("/history")
async def get_history(
    request: HistoryRequest,
    user: Dict = Depends(get_current_user)
):
    """Get the history for a specific session"""
    
    # Validate the user
    if user.get("sub") != request.user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    try:
        # Get the session history
        history = await get_session_history(request.session_id)
        
        # Return formatted results
        return {
            "session_id": request.session_id,
            "history": [
                {
                    "input": item.get("input_text", ""),
                    "output": item.get("output", ""),
                    "type": item.get("type", ""),
                    "timestamp": item.get("timestamp", "").isoformat() 
                    if isinstance(item.get("timestamp"), datetime) 
                    else item.get("timestamp", ""),
                    "id": str(item.get("_id", ""))
                }
                for item in history
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)