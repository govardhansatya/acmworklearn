# backend/generators/game_script_generator.py
from datetime import datetime
from typing import Dict, Any, Optional, List

async def generate_game_script(
    db,
    user_id: str,
    input_text: str,
    session_id: Optional[str] = None,
    previous_output: Optional[str] = None,
    gemini_generate_fn = None
):
    """Generate game scripts based on user input
    
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
    # Determine script type (dialogue, narrative, quest, etc)
    script_types = ["dialogue", "quest", "narrative", "cutscene", "tutorial"]
    detected_type = next((t for t in script_types if t in input_text.lower()), "general")
    
    # Determine if this is a continuation request
    is_continuation = bool(previous_output) and any(
        kw in input_text.lower() for kw in [
            "continue", "add more", "extend", "next scene",
            "next act", "keep going", "what happens next"
        ]
    )
    
    # Build the appropriate prompt
    if is_continuation and previous_output:
        prompt = f"""Continue this game script:
{previous_output}

Next part based on: {input_text}

Maintain the same tone, style, and characters. Make sure the continuation feels natural.
"""
    else:
        prompt = f"""Write a creative game script based on this idea: {input_text}

Create a {detected_type} script that includes:
- Clear character identification for dialogue (if applicable)
- Setting descriptions
- Stage directions where needed
- Emotions and tone indicators

Make it engaging and suitable for a video game context.
"""
    
    # Generate the script content
    output = await gemini_generate_fn(prompt)
    
    # Extract characters from the script (basic detection)
    characters = extract_characters(output)
    
    # Save to database if db connection is provided
    if db:
        # Create document to store
        entry = {
            "user_id": user_id,
            "session_id": session_id,
            "type": "game_script",
            "script_type": detected_type,
            "input_text": input_text,
            "output": output,
            "characters": characters,
            "timestamp": datetime.utcnow(),
            "mode": "extend" if is_continuation else "new"
        }
        
        # Insert into the database
        await db.creative_outputs.insert_one(entry)
    
    # Return the generated content and metadata
    return {
        "output": output,
        "type": "game_script",
        "script_type": detected_type,
        "characters": characters,
        "mode": "extend" if is_continuation else "new"
    }

def extract_characters(script_text: str) -> List[str]:
    """Extract character names from script text
    
    Basic implementation that looks for common script patterns like "NAME:" or "NAME (emotion):"
    
    Args:
        script_text: The generated script text
        
    Returns:
        List of unique character names found
    """
    import re
    
    # Look for patterns like "CHARACTER:" or "CHARACTER (emotion):" at line starts
    character_pattern = re.compile(r'^([A-Z][A-Za-z\s]+)(\s*\([^)]+\))?\s*:', re.MULTILINE)
    matches = character_pattern.findall(script_text)
    
    # Extract just the character names and remove duplicates
    characters = list(set(match[0].strip() for match in matches))
    
    return characters