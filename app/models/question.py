from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class QuestionGenerationRequest(BaseModel):
    """Request model for AI to generate questions"""
    session_id: str
    skills_analysis: dict = Field(..., description="AI generated skills analysis")
    interview_prefernces: Optional[dict] = Field(default_factory=dict)
    question_count: int = Field(default=10, le=5, ge=20, description="Number of questions to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "skills_analysis": {
                    "primary_domain": "Backend Development",
                    "technical_skills": ["Python", "MERN", "AWS"],
                    "experience_level": "Intermediate"
                },
                "interview_prefernces": {
                    "interview_type": "technical",
                    "difficulty_level": "medium",
                },
                "question_count": 10
            }
        }

class DyanmicQuestion(BaseModel):
    """AI generated question model"""
    question: str = Field(..., description="AI generated question")

    # everything below is ai determined
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="AI assigned metadata like type, difficuilty etc")

    generated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "How to optimize a Django application with 1M requests per day",
                "metdata": {
                    "type": "technical",
                    "difficuilty": "medium",
                    "skills_tested": ["Django, scalibility, optimization"],
                    "estimated_time": "5 minutes",
                    "focus_area": "System Design",
                    "reasoning": "Tests practical application with optimizations"
                },
                "generated_at": "2024-01-01T10:00:00"
            }
        }

class FollowUpQuestionRequest(BaseModel):
    """Request for AI to generate follow up questions"""
    original_question: dict = Field(..., description="Original question asked")
    original_response: str = Field(..., description="Candidate's answer")
    skills_context: str = Field(..., description="Candidate's skills for context")

    class Config:
        json_schema_extra = {
            "example": {
                "original_question": {
                    "question": "Tell me about your experience",
                    "type": "technical"
                },
                "candidate_response": "I have used Python for backend development and AIML",
                "skills_context": {
                    "primary_domain": "Software and AIML",
                    "technical_skillls": ["Python", "AIML"]
                }
            }
        }

class FollowUpQuestion(BaseModel):
    """AI generated follw up questions"""
    followup_question: str = Field(..., description="AI generated follow up question")
    reasoning: str = Field(..., description="Why AI decied to ask this follow up")

    # AI determines if this adds value
    is_necessary: bool = Field(default=True, description="AI's descision if this follow up is needed or not")
    
    class Config:
        json_schema_extra = {
            "example": {
                "followup_question": "Can you describe a specific challenge you faced while scaling a Django application?",
                "reasoning": "Candidate mentioned Django experience but didn't provide specific examples",
                "is_necessary": True
            }
        }

class QuestionAdaptation(BaseModel):
    """AI adapts questions based on performance"""
    session_id: str
    current_performance: dict = Field(..., description="AI analysis of current performance")
    remaining_questions: List[dict] = Field(..., description="Questions not yet asked")

    adaptation_strategy: Optional[str] = Field(None, description="AI's adaption approach")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "current_performance": {
                    "average_score": 8,
                    "strong_areas": ["Python", "AIML", "Databases"],
                    "weak_areas": ["System Design"]
                },
                "remaining_questions": [
                    {"question": "Describe micrroservice architechture", "type": "technical"},
                ],
                "adaptation_strategy": "increase difficuilty in string areas"
            }
        }

class AdaptedQuestions(BaseModel):
    """AI adapted questions based on performance"""

    adapted_questions: List[dict] = Field(..., description="Adapted questions")
    adaptation_reasoning: Optional[str] = Field(None, description="AI's adaption approach")

    class Config:
        json_schema_extra = {
            "example": {
                "adapted_questions": [
                    {
                        "question": "Design a distributed cache system handling 100k RPS",
                        "reason": "Increased difficulty in strong areas"
                    }
                ],
                "adaptation_reasoning": "Candidate performing well on mid-level questions, advancing to harder topics"
            }
        }