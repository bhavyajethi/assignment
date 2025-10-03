from typing import Dict, List, Any, Optional
from datetime import datetime

from .question_bank import QuestionBank
from ..services.ai_service import AIService


class InterviewEngine:
    """AI-driven interview engine that dynamically manages the entire interview flow."""
    
    def __init__(self):
        self.question_bank = QuestionBank()
        self.ai_service = AIService()
    
    async def initialize_interview(
        self, 
        skills_analysis: Dict[str, Any], 
        interview_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Initialize interview using AI to set up everything dynamically."""
        try:
            # Let AI decide interview structure and approach
            interview_plan = await self.ai_service.create_interview_plan(
                skills_analysis=skills_analysis,
                preferences=interview_preferences or {}
            )
            
            # Generate initial questions using AI
            questions = await self.question_bank.generate_personalized_questions(
                skills_analysis=skills_analysis,
                experience_level=skills_analysis.get('experience_level', 'medium'),
                interview_type=interview_plan.get('interview_type', 'general'),
                question_count=interview_plan.get('question_count', 10)
            )
            
            # Generate AI greeting
            greeting = await self.ai_service.generate_interview_greeting(
                skills_analysis=skills_analysis,
                interview_plan=interview_plan
            )
            
            return {
                'interview_plan': interview_plan,
                'questions': questions,
                'greeting': greeting,
                'total_questions': len(questions),
                'estimated_duration': interview_plan.get('estimated_duration', '30 minutes'),
                'focus_areas': interview_plan.get('focus_areas', [])
            }
            
        except Exception as e:
            raise Exception(f"Error initializing interview: {str(e)}")
    
    async def process_response(
        self,
        question: Dict[str, Any],
        response: str,
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process candidate response and determine next action using AI."""
        try:
            # Analyze the response using AI
            response_analysis = await self.ai_service.analyze_candidate_response(
                question=question,
                response=response,
                skills_context=session_context.get('skills_analysis', {}),
                interview_context=session_context.get('responses', [])
            )
            
            # Let AI decide next action
            next_action = await self.ai_service.determine_next_interview_action(
                response_analysis=response_analysis,
                current_progress=session_context,
                remaining_questions=session_context.get('questions', [])
            )
            
            return {
                'response_analysis': response_analysis,
                'next_action': next_action,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback: continue with next question
            return {
                'response_analysis': {'score': 5, 'feedback': 'Response recorded'},
                'next_action': {'action': 'next_question', 'reason': 'ai_analysis_failed'},
                'error': str(e)
            }
    
    async def should_continue_interview(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to determine if interview should continue or end."""
        try:
            # Let AI analyze current interview state and decide
            continue_decision = await self.ai_service.should_continue_interview(
                responses=session_data.get('responses', []),
                skills_analysis=session_data.get('skills_analysis', {}),
                interview_progress=self._calculate_progress(session_data),
                time_elapsed=self._calculate_time_elapsed(session_data)
            )
            
            return continue_decision
            
        except Exception as e:
            # Default: continue if less than 15 questions answered
            responses_count = len(session_data.get('responses', []))
            return {
                'should_continue': responses_count < 15,
                'reason': 'fallback_decision',
                'confidence': 'low',
                'error': str(e)
            }
    
    async def get_next_question(
        self,
        session_data: Dict[str, Any],
        last_response_analysis: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get next question using AI to adapt based on performance."""
        try:
            current_index = session_data.get('current_question_index', 0)
            questions = session_data.get('questions', [])
            
            # If we have remaining pre-generated questions
            if current_index < len(questions):
                next_question = questions[current_index]
                
                # Let AI modify or replace the question based on performance
                if last_response_analysis:
                    adapted_question = await self.ai_service.adapt_question_based_on_performance(
                        planned_question=next_question,
                        performance_analysis=last_response_analysis,
                        skills_context=session_data.get('skills_analysis', {})
                    )
                    return adapted_question
                
                return next_question
            
            # Generate new question on the fly using AI
            else:
                dynamic_question = await self.ai_service.generate_dynamic_question(
                    session_context=session_data,
                    performance_so_far=last_response_analysis
                )
                return dynamic_question
                
        except Exception as e:
            return None
    
    async def generate_interview_conclusion(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-driven interview conclusion and closing remarks."""
        try:
            conclusion = await self.ai_service.generate_interview_conclusion(
                responses=session_data.get('responses', []),
                skills_analysis=session_data.get('skills_analysis', {}),
                interview_duration=self._calculate_time_elapsed(session_data)
            )
            
            return conclusion
            
        except Exception as e:
            return {
                'closing_message': 'Thank you for completing the interview. Your responses will be analyzed shortly.',
                'next_steps': 'Please wait while we generate your personalized feedback report.',
                'error': str(e)
            }
    
    def _calculate_progress(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate current interview progress."""
        questions = session_data.get('questions', [])
        responses = session_data.get('responses', [])
        current_index = session_data.get('current_question_index', 0)
        
        total_questions = len(questions)
        questions_answered = len(responses)
        
        return {
            'total_questions': total_questions,
            'questions_answered': questions_answered,
            'current_question_number': current_index + 1,
            'completion_percentage': (questions_answered / total_questions * 100) if total_questions > 0 else 0,
            'questions_remaining': max(0, total_questions - questions_answered)
        }
    
    def _calculate_time_elapsed(self, session_data: Dict[str, Any]) -> str:
        """Calculate time elapsed since interview start."""
        try:
            start_time_str = session_data.get('start_time')
            if not start_time_str:
                return "0 minutes"
            
            start_time = datetime.fromisoformat(start_time_str)
            current_time = datetime.now()
            elapsed = current_time - start_time
            elapsed_minutes = int(elapsed.total_seconds() / 60)
            
            return f"{elapsed_minutes} minutes"
            
        except Exception:
            return "Unknown duration"