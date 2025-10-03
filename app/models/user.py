from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """User model - data extracted by the ai model"""

    session_id: str = Field(..., description="Unique session idetifier")
    name: Optional[str] = Field(None, description="Candidate name extracted by AI")
    email: Optional[str] = Field(None, description="Email extracted by AI")
    phone: Optional[str] = Field(None, description="Phone number extracted by AI")
    Location: Optional[str] = Field(None, description="Location extracted by AI")

    # Fields determined by the ai dynamically
    profile_summary: Optional[str] = Field(None, description="Profile summary extracted by AI")
    total_experience: Optional[str] = Field(None, description="Total experience extracted by AI")

    created_at: datetime = Field(default_factory= datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123-session",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "Location": "New York, USA",
                "profile_summary": "A summary of the candidate's experience and skills.",
                "total_experience": "3 years",
                "created_at": "2024-01-01T10:00:00",
            }
        }

class ResumeData(BaseModel):
    """Resume Data Model - all fields parsed and structured by AI"""

    session_id: str
    raw_text: str = Field(..., description="Raw text extracted from the resume")

    # AI determines structure and extracts these dynamically 
    parsed_data: dict = Field(default_factory=dict, description="AI-parsed strcutured data")

    # MetaData
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    word_count: Optional[int] = None
    uploaded_at: datetime = Field(default_factory= datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "raw_text": "Full resume text",
                "parsed_data": {
                    "name": "John Doe",
                    "experience": [],
                    "education": [],
                    "skills": []
                },
                "file_name": "resume.pdf",
                "file_type": "pdf",
                "word_count": 450
            }
        }