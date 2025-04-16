# backend/generators/poetry_generator.py
from datetime import datetime
from typing import Dict, Any

async def generate_poetry(
    db,
    user_id: str,
    input_text: str,
    session_id: str = None,
    previous_output: str = None,
    gemini_generate_fn = None
):
    """Generate poetry based on user input
    
    Args:
        db: MongoDB database connection
        user_id: User ID requesting the generation
        input_text: Text prompt from the user
        session_id: Optional session ID for continuing existing work
        previous_output: Previous output to continue from
        gemini_generate_fn: Function to call Gemini API
        
    Returns:
        Dict containing the generated output and metadata
    """
    # Determine if this is a continuation request
    is_continuation = bool(previous_output) and any(
        kw in input_text.lower() for kw in [
            "continue", "add more", "extend", "another verse", 
            "next stanza", "keep going"
        ]
    )
    
    # Build the appropriate prompt
    if is_continuation and previous_output:
        prompt = f"Continue this poem:\n{previous_output}\n\nContinue with: {input_text}"
    else:
        prompt = f"Write a poem inspired by this prompt: {input_text}"
    
    # Generate the poetry content
    output = await gemini_generate_fn(prompt)
    
    # Save to database if db connection is provided
    if db:
        # Create document to store
        entry = {
            "user_id": user_id,
            "session_id": session_id,
            "type": "poetry",
            "input_text": input_text,
            "output": output,
            "timestamp": datetime.utcnow(),
            "mode": "extend" if is_continuation else "new"
        }
        
        # Insert into the database
        await db.creative_outputs.insert_one(entry)
    
    # Return the generated content and metadata
    return {
        "output": output,
        "type": "poetry",
        "mode": "extend" if is_continuation else "new"
    }