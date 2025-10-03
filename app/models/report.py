from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class ReportGenerationRequest(BaseModel):
    """Request for AI to generate the report"""
    session_id: str
    interview_data: dict = Field(..., description="Complete interview session data")
    skills_analysis: dict = Field(..., description="AI analyzed skills analysis")
    all_responses: List[dict] = Field(..., description="All Q&A from interview")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "interview_data": {
                    "duration": "30 minutes",
                    "questions_answered": 10,
                    "completion_rate": "100%",
                },
                "skills_analysis": {
                    "primary_domain": "AI Development",
                    "experience_level": "mid"
                },
                "all_responses": [
                    {
                        "question": "Describe your experience with Python",
                        "answer": "I have 3 years of experience with Python",
                    }
                ]
            }
        }

class InterviewReport(BaseModel):
    """AI generated interview report"""

    report_id: str = Field(..., description="Unique report identifier")
    session_id: str
    generated_at: datetime = Field(default_factory=datetime.now)

    # AI generated sections
    ai_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="AI analysis of the interview"
    )

    # Candidate info extracted by the AI
    candidate_info: Dict[str, Any] = Field(None, description="AI extracted candidate details")

    # Interview summary
    interview_summary: Dict[str, Any] = Field(None, description="AI generated interview summary")

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report_abc123",
                "session_id": "abc123",
                "generated_at": "2024-01-01T10:00:00",
                "ai_analysis": {
                    "overall_score": 8,
                    "performance_level": "Good",
                    "key_strengths": ["Communication", "Smart"],
                    "improvement_areas": ["System Design", "Concrete examples"],
                    "hiring_recommendation": "Proceed to next round",
                    "detailed_feedback": "Candidate demonstrated solid technical knowledge..."
                },
                "candidate_info": {
                    "name": "John Doe",
                    "experience_level": "mid"
                },
                "interview_summary": {
                    "duration": "30 minutes",
                    "questions_answered": 10,
                    "completion_rate": "100%"
                }
            }
        }

class PerformanceAnalysis(BaseModel):
    """AI's performance analysis"""
    analysis_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="AI determines what to analyze and how to score"
    )

    generated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_data": {
                    "technical_competency": {
                        "score": 8,
                        "assessment": "Strong technical knowledge"
                    },
                    "communication_skills": {
                        "score": 7,
                        "assessment": "Clear articulation, could be more concise"
                    },
                    "problem_solving_approach": {
                        "score": 8,
                        "assessment": "Systematic approach to problems"
                    },
                    "domain_expertise": {
                        "areas": ["Backend", "API's", "Databases"],
                        "depth": "Good understanding with practical experience"
                    }
                },
                "generated_at": "2024-01-01T11:00:00"
            }
        }

class DetailedFeedback(BaseModel):
    """AI-generated detailed question-by-question feedback"""

    session_id: str
    question_feedbacks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="AI analysis for each question - structure is dynamic"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "question_feedbacks": [
                    {
                        "question_number": 1,
                        "question": "Tell me about work experience",
                        "response_summary": "Described 3 years of Python work...",
                        "ai_evaluation": {
                            "score": 8,
                            "strengths": ['Specific examples', 'Good timeline'],
                            "improvements": ["Could mention more frameworks"],
                            "feedback": "Strong response with clear examples"
                        }
                    }
                ]
            }
        }

class RecommendationReport(BaseModel):
    """AI generated recommendation"""
    session_id: str

    # All generated by AI 
    recommendations: Dict[str, Any] = Field(
        default_factory=dict,
        description="AI generated recommendation"
    )