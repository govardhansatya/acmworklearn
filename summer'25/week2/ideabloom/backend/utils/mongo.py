# backend/utils/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "creative_buddy")

# Create client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collection references
users_collection = db["users"]
outputs_collection = db["creative_outputs"]
history_collection = db["history"]
feedback_collection = db["feedback"]

async def save_creative_output(
    user_id: str,
    input_text: str,
    output: str,
    output_type: str,
    session_id: Optional[str] = None,
    mode: str = "new",
    metadata: Optional[Dict[str, Any]] = None,
    embedding: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Save a creative output to the database
    
    Args:
        user_id: User ID that generated the output
        input_text: Original input text from the user
        output: Generated output text
        output_type: Type of output (poetry, melody, script)
        session_id: Optional session ID for continuing work
        mode: Generation mode (new or extend)
        metadata: Additional metadata for the output
        embedding: Vector embedding for semantic search
        
    Returns:
        Dictionary with inserted document information
    """
    # Create a new session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Prepare the document
    document = {
        "user_id": user_id,
        "session_id": session_id,
        "input_text": input_text,
        "output": output,
        "type": output_type,
        "mode": mode,
        "timestamp": datetime.utcnow(),
        "embedding": embedding or []
    }
    
    # Add any additional metadata
    if metadata:
        document.update(metadata)
    
    # Insert the document
    result = await outputs_collection.insert_one(document)
    
    # Return useful information
    return {
        "output_id": str(result.inserted_id),
        "session_id": session_id,
        "timestamp": document["timestamp"].isoformat()
    }

async def get_session_history(
    session_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get the history of a specific session
    
    Args:
        session_id: The session ID to retrieve history for
        limit: Maximum number of history items to return
        
    Returns:
        List of history items for the session, ordered by timestamp
    """
    cursor = outputs_collection.find(
        {"session_id": session_id}
    ).sort("timestamp", 1).limit(limit)
    
    return await cursor.to_list(length=limit)

async def save_user_feedback(
    user_id: str,
    output_id: str,
    feedback_text: str,
    rating: Optional[int] = None
) -> bool:
    """Save user feedback for a generated output
    
    Args:
        user_id: User ID providing the feedback
        output_id: Output ID the feedback is for
        feedback_text: Text feedback from the user
        rating: Optional numerical rating (e.g., 1-5)
        
    Returns:
        Boolean indicating success
    """
    # Prepare the feedback document
    feedback = {
        "user_id": user_id,
        "output_id": output_id,
        "feedback": feedback_text,
        "timestamp": datetime.utcnow()
    }
    
    # Add rating if provided
    if rating is not None:
        feedback["rating"] = rating
    
    # Insert the feedback
    await feedback_collection.insert_one(feedback)
    
    # Also update the original output document
    update_result = await outputs_collection.update_one(
        {"_id": output_id},
        {"$set": {"has_feedback": True}}
    )
    
    return update_result.modified_count > 0

async def get_user_outputs(
    user_id: str,
    output_type: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Get outputs for a specific user
    
    Args:
        user_id: User ID to get outputs for
        output_type: Optional type filter (poetry, melody, script)
        limit: Maximum number of outputs to return
        skip: Number of outputs to skip (for pagination)
        
    Returns:
        List of user outputs
    """
    # Build query
    query = {"user_id": user_id}
    if output_type:
        query["type"] = output_type
    
    # Execute query
    cursor = outputs_collection.find(query).sort(
        "timestamp", -1  # Newest first
    ).skip(skip).limit(limit)
    
    return await cursor.to_list(length=limit)