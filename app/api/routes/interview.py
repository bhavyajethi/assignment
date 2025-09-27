from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ...dependencies import get_session
from ...core.interview_engine import InterviewEngine
from ...services.ai_service import AIService
from ...config import settings

router = APIRouter()

# Pydantic models for request/response
class InterviewResponse(BaseModel):
    response: str
    
class InterviewPreferences(BaseModel):
    interview_type: Optional[str] = "general"  # general, technical, behavioral
    difficulty: Optional[str] = "medium"  # easy, medium, hard
    duration_minutes: Optional[int] = 30

@router.post("/start-interview/{session_id}")
async def start_interview(
    session_id: str,
    preferences: Optional[InterviewPreferences] = None
):
    """
    Start the interview session.
    AI will greet the candidate and ask if they're ready.
    """
    try:
        session_data = get_session(session_id)
        
        # Check if resume analysis is complete
        if not session_data.get('skills_analysis'):
            raise HTTPException(
                status_code=400,
                detail="Please upload and analyze your resume before starting the interview."
            )
        
        if session_data.get('interview_started'):
            raise HTTPException(
                status_code=400,
                detail="Interview already started for this session."
            )
        
        # Initialize interview engine
        engine = InterviewEngine()
        ai_service = AIService()
        
        # Set preferences
        prefs = preferences or InterviewPreferences()
        session_data['interview_preferences'] = prefs.dict()
        
        # Generate personalized questions based on skills analysis
        questions = await engine.generate_questions(
            skills_analysis=session_data['skills_analysis'],
            interview_type=prefs.interview_type,
            difficulty=prefs.difficulty
        )
        
        # Generate AI greeting
        greeting = await ai_service.generate_interview_greeting(
            skills_analysis=session_data['skills_analysis'],
            candidate_name=session_data.get('resume_data', {}).get('name', 'candidate')
        )
        
        # Update session
        session_data.update({
            'interview_started': True,
            'interview_ended': False,
            'questions': questions,
            'current_question_index': 0,
            'responses': [],
            'start_time': datetime.now().isoformat(),
            'ai_greeting': greeting
        })
        
        return {
            "success": True,
            "message": "Interview started successfully!",
            "session_id": session_id,
            "ai_message": greeting,
            "total_questions": len(questions),
            "estimated_duration": f"{prefs.duration_minutes} minutes",
            "ready_to_proceed": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting interview: {str(e)}"
        )


@router.post("/proceed-interview/{session_id}")
async def proceed_with_interview(session_id: str):
    """
    Proceed with interview after user confirms they're ready.
    Returns the first question.
    """
    try:
        session_data = get_session(session_id)
        
        if not session_data.get('interview_started'):
            raise HTTPException(
                status_code=400,
                detail="Interview not started. Please start the interview first."
            )
        
        questions = session_data.get('questions', [])
        if not questions:
            raise HTTPException(
                status_code=500,
                detail="No questions generated. Please restart the interview."
            )
        
        # Get first question
        current_index = session_data.get('current_question_index', 0)
        current_question = questions[current_index]
        
        return {
            "session_id": session_id,
            "question_number": current_index + 1,
            "total_questions": len(questions),
            "question": current_question['question'],
            "question_type": current_question.get('type', 'general'),
            "expected_duration": "2-3 minutes",
            "ai_message": f"Great! Let's begin. Here's your first question:\n\n{current_question['question']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error proceeding with interview: {str(e)}"
        )


@router.post("/submit-response/{session_id}")
async def submit_response(session_id: str, response_data: InterviewResponse):
    """
    Submit candidate response and get next question or AI follow-up.
    """
    try:
        session_data = get_session(session_id)
        
        if not session_data.get('interview_started') or session_data.get('interview_ended'):
            raise HTTPException(
                status_code=400,
                detail="Interview not active."
            )
        
        questions = session_data.get('questions', [])
        current_index = session_data.get('current_question_index', 0)
        
        if current_index >= len(questions):
            raise HTTPException(
                status_code=400,
                detail="All questions completed."
            )
        
        # Store the response
        current_question = questions[current_index]
        response_entry = {
            "question_number": current_index + 1,
            "question": current_question['question'],
            "question_type": current_question.get('type'),
            "response": response_data.response,
            "timestamp": datetime.now().isoformat()
        }
        
        session_data['responses'].append(response_entry)
        
        # Analyze response and determine next action
        ai_service = AIService()
        analysis = await ai_service.analyze_response(
            question=current_question,
            response=response_data.response,
            skills_context=session_data['skills_analysis']
        )
        
        # Check if we need a follow-up or should move to next question
        should_followup = analysis.get('needs_followup', False)
        follow_up_question = analysis.get('followup_question')
        
        if should_followup and follow_up_question:
            # Ask follow-up question
            return {
                "session_id": session_id,
                "type": "followup",
                "question_number": current_index + 1,
                "followup_question": follow_up_question,
                "ai_message": f"Thank you for that response. {follow_up_question}",
                "progress": f"{current_index + 1}/{len(questions)}"
            }
        else:
            # Move to next question
            next_index = current_index + 1
            session_data['current_question_index'] = next_index
            
            if next_index >= len(questions):
                # Interview completed
                return await _complete_interview(session_data, session_id)
            else:
                # Get next question
                next_question = questions[next_index]
                return {
                    "session_id": session_id,
                    "type": "next_question",
                    "question_number": next_index + 1,
                    "total_questions": len(questions),
                    "question": next_question['question'],
                    "question_type": next_question.get('type'),
                    "ai_message": f"Great answer! Let's move to the next question:\n\n{next_question['question']}",
                    "progress": f"{next_index + 1}/{len(questions)}"
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing response: {str(e)}"
        )


async def _complete_interview(session_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """Complete the interview and prepare for report generation."""
    session_data.update({
        'interview_ended': True,
        'end_time': datetime.now().isoformat()
    })
    
    # Calculate interview duration
    start_time = datetime.fromisoformat(session_data['start_time'])
    end_time = datetime.fromisoformat(session_data['end_time'])
    duration_minutes = int((end_time - start_time).total_seconds() / 60)
    
    return {
        "session_id": session_id,
        "type": "interview_complete",
        "message": "Congratulations! You've completed the interview.",
        "ai_message": "Thank you for completing the interview! I'm now analyzing your responses to generate a personalized feedback report.",
        "summary": {
            "questions_answered": len(session_data['responses']),
            "duration_minutes": duration_minutes,
            "completion_time": session_data['end_time']
        },
        "report_ready": False,
        "next_step": "generating_report"
    }


@router.get("/interview-status/{session_id}")
async def get_interview_status(session_id: str):
    """Get current interview status and progress."""
    try:
        session_data = get_session(session_id)
        
        return {
            "session_id": session_id,
            "interview_started": session_data.get('interview_started', False),
            "interview_ended": session_data.get('interview_ended', False),
            "current_question": session_data.get('current_question_index', 0) + 1,
            "total_questions": len(session_data.get('questions', [])),
            "responses_given": len(session_data.get('responses', [])),
            "start_time": session_data.get('start_time'),
            "estimated_time_remaining": "5-10 minutes"  # Simple estimation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting interview status: {str(e)}"
        )


@router.post("/end-interview/{session_id}")
async def end_interview_early(session_id: str):
    """End interview early if user wants to stop."""
    try:
        session_data = get_session(session_id)
        
        if not session_data.get('interview_started'):
            raise HTTPException(
                status_code=400,
                detail="No active interview to end."
            )
        
        if session_data.get('interview_ended'):
            return {"message": "Interview already ended", "session_id": session_id}
        
        # End interview
        return await _complete_interview(session_data, session_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ending interview: {str(e)}"
        )