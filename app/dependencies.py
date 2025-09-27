from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile
import os
from .config import settings


async def validate_file_upload(file: UploadFile) -> UploadFile:
    """Validate uploaded resume file."""
    
    # Check if file exists
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file extension
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Supported types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    return file


def get_groq_client():
    """Get Groq AI client instance."""
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Groq API key not configured"
        )
    
    from groq import Groq
    return Groq(api_key=settings.GROQ_API_KEY)


def create_session_storage() -> Dict[str, Any]:
    """Create in-memory session storage for interview data."""
    return {
        "resume_data": None,
        "skills_analysis": None,
        "questions": [],
        "responses": [],
        "current_question_index": 0,
        "interview_started": False,
        "interview_ended": False,
        "start_time": None,
        "end_time": None
    }


# Global session storage (in production, use Redis or database)
session_storage: Dict[str, Dict[str, Any]] = {}


def get_session(session_id: str) -> Dict[str, Any]:
    """Get or create session data."""
    if session_id not in session_storage:
        session_storage[session_id] = create_session_storage()
    return session_storage[session_id]


def clear_session(session_id: str) -> None:
    """Clear session data."""
    if session_id in session_storage:
        del session_storage[session_id]