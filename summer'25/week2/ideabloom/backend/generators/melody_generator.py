# backend/generators/melody_generator.py
from datetime import datetime
from typing import Dict, Any, Optional

async def generate_melody(
    db,
    user_id: str,
    input_text: str,
    session_id: Optional[str] = None,
    previous_output: Optional[str] = None,
    gemini_generate_fn = None
):
    """Generate melodic descriptions or ABC notation based on user input
    
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
            "continue", "add more", "extend", "next part",
            "next measure", "keep going", "build on"
        ]
    )
    
    # Determine if we should generate ABC notation or a descriptive melody
    is_abc_notation = "abc notation" in input_text.lower() or "sheet music" in input_text.lower()
    
    # Build the appropriate prompt
    if is_continuation and previous_output:
        if is_abc_notation:
            prompt = f"Continue this melody in ABC notation format:\n{previous_output}\n\nExtend with: {input_text}"
        else:
            prompt = f"Continue this melodic description:\n{previous_output}\n\nWith these additional elements: {input_text}"
    else:
        if is_abc_notation:
            prompt = f"Create a melody in ABC notation format based on this theme: {input_text}"
        else:
            prompt = f"Describe a melodic theme based on: {input_text}. Include details about mood, tempo, key, and instrumentation."
    
    # Generate the melody content
    output = await gemini_generate_fn(prompt)
    
    # Save to database if db connection is provided
    if db:
        # Create document to store
        entry = {
            "user_id": user_id,
            "session_id": session_id,
            "type": "melody",
            "input_text": input_text,
            "output": output,
            "notation_type": "abc" if is_abc_notation else "descriptive",
            "timestamp": datetime.utcnow(),
            "mode": "extend" if is_continuation else "new"
        }
        
        # Insert into the database
        await db.creative_outputs.insert_one(entry)
    
    # Return the generated content and metadata
    return {
        "output": output,
        "type": "melody",
        "notation_type": "abc" if is_abc_notation else "descriptive",
        "mode": "extend" if is_continuation else "new"
    }