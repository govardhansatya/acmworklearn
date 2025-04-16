# backend/utils/utils.py
import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load generative model
model = genai.GenerativeModel("gemini-pro")
embed_model = genai.get_model("models/embedding-001")

def detect_extend_intent(input_text: str) -> bool:
    """Detect if the user's prompt indicates an intent to extend previous output.
    
    Args:
        input_text: The user's input text
        
    Returns:
        Boolean indicating if this is likely an extension request
    """
    extend_keywords = [
        "continue", "add more", "extend", "next part",
        "follow up", "carry on", "build on", "next scene",
        "another verse", "keep going", "what happens next"
    ]
    return any(kw in input_text.lower() for kw in extend_keywords)

def build_prompt(input_text: str, content_type: str, context: str = "") -> str:
    """Constructs a prompt for generation based on content type and context.
    
    Args:
        input_text: The user's input text
        content_type: The type of content to generate (poetry, melody, script)
        context: Optional previous output to continue from
        
    Returns:
        Formatted prompt string for the AI model
    """
    # Check if this is an extension request with context
    is_extend = bool(context) and detect_extend_intent(input_text)
    
    # Build type-specific prompts
    if content_type == "poetry":
        if is_extend:
            return f"Continue this poem:\n{context}\n\nContinue with: {input_text}"
        return f"Write a creative poem based on: {input_text}"
        
    elif content_type == "melody":
        if is_extend:
            return f"Continue this melody description:\n{context}\n\nWith: {input_text}"
        return f"Generate a melodic theme or description based on: {input_text}"
        
    elif content_type == "script":
        if is_extend:
            return f"Continue this game script:\n{context}\n\nNext part based on: {input_text}"
        return f"Write a creative game script based on this idea: {input_text}"
    
    # Default case - just use the input text
    return input_text

async def generate_text_gemini(prompt: str) -> str:
    """Generates content using Gemini Pro.
    
    Args:
        prompt: The prompt for generation
        
    Returns:
        Generated text from the model
        
    Raises:
        Exception: If generation fails
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Text Generation Error] {e}")
        raise Exception(f"Error generating content: {str(e)}")

async def embed_text_gemini(text: str) -> List[float]:
    """Generates embeddings using Gemini Embed.
    
    Args:
        text: Text to generate embeddings for
        
    Returns:
        List of embedding values
    """
    try:
        result = embed_model.embed_content(
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    except Exception as e:
        print(f"[Gemini Embedding Error] {e}")
        return []

async def find_similar_outputs(
    db, 
    query_text: str, 
    user_id: Optional[str] = None, 
    content_type: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Find similar outputs based on semantic similarity
    
    Args:
        db: MongoDB database connection
        query_text: Text to find similar outputs for
        user_id: Optional user ID to filter results
        content_type: Optional content type to filter results
        limit: Maximum number of results to return
        
    Returns:
        List of similar outputs with similarity scores
    """
    try:
        # Generate embedding for the query text
        query_embedding = await embed_text_gemini(query_text)
        
        if not query_embedding:
            return []
            
        # Build the aggregation pipeline
        pipeline = [
            {
                "$search": {
                    "index": "creative_outputs_vector",
                    "knnBeta": {
                        "vector": query_embedding,
                        "path": "embedding",
                        "k": limit * 2,  # Get more than we need for filtering
                    }
                }
            }
        ]
        
        # Add filters if provided
        match_stage = {}
        if user_id:
            match_stage["user_id"] = user_id
        if content_type:
            match_stage["type"] = content_type
            
        if match_stage:
            pipeline.append({"$match": match_stage})
            
        # Limit and project
        pipeline.extend([
            {"$limit": limit},
            {
                "$project": {
                    "_id": 1,
                    "type": 1,
                    "input_text": 1,
                    "output": 1,
                    "timestamp": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ])
        
        # Execute the query
        results = await db.creative_outputs.aggregate(pipeline).to_list(limit)
        return results
        
    except Exception as e:
        print(f"[Vector Search Error] {e}")
        return []