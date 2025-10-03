from typing import Dict, List, Any, Optional
from ..services.ai_service import AIService


class QuestionBank:
    """AI-driven question generation that creates personalized questions dynamically."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_personalized_questions(
        self, 
        skills_analysis: Dict[str, Any],
        experience_level: str = "medium",
        interview_type: str = "general",
        question_count: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate completely personalized questions using AI based on candidate's actual skills."""
        try:
            # Let AI generate all questions based on the candidate's specific profile
            questions = await self.ai_service.generate_interview_questions(
                skills_analysis=skills_analysis,
                experience_level=experience_level,
                interview_type=interview_type,
                question_count=question_count
            )
            
            return questions
            
        except Exception as e:
            # Fallback: Ask AI for basic questions if personalized generation fails
            try:
                basic_questions = await self.ai_service.generate_basic_interview_questions(question_count)
                return basic_questions
            except:
                # Last resort: Return minimal hardcoded questions
                return self._emergency_fallback_questions()
    
    async def generate_followup_question(
        self, 
        original_question: Dict[str, Any], 
        candidate_response: str,
        skills_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI-driven follow-up question based on candidate's response."""
        try:
            followup = await self.ai_service.generate_followup_question(
                original_question, candidate_response, skills_context
            )
            return followup
            
        except Exception as e:
            return None
    
    async def adapt_question_difficulty(
        self, 
        current_performance: Dict[str, Any],
        remaining_questions: List[Dict[str, Any]],
        skills_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use AI to adapt remaining questions based on current performance."""
        try:
            adapted_questions = await self.ai_service.adapt_questions_to_performance(
                current_performance, remaining_questions, skills_analysis
            )
            return adapted_questions
            
        except Exception as e:
            # Return original questions if adaptation fails
            return remaining_questions
    
    def _emergency_fallback_questions(self) -> List[Dict[str, Any]]:
        """Emergency fallback questions if AI fails completely."""
        return [
            {
                'question': 'Tell me about yourself and your background.',
                'type': 'general',
                'difficulty': 'easy',
                'estimated_time': '3 minutes',
                'skills_tested': ['communication'],
                'generated_by': 'fallback'
            },
            {
                'question': 'What interests you most about this role?',
                'type': 'general', 
                'difficulty': 'easy',
                'estimated_time': '2 minutes',
                'skills_tested': ['motivation'],
                'generated_by': 'fallback'
            },
            {
                'question': 'Describe a challenging project you worked on.',
                'type': 'behavioral',
                'difficulty': 'medium',
                'estimated_time': '4 minutes',
                'skills_tested': ['problem_solving'],
                'generated_by': 'fallback'
            }
        ]