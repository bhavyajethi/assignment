import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

from ...dependencies import validate_file_upload, get_session
from ...core.resume_parser import ResumeParser
from ...core.skill_analyzer import SkillAnalyzer
from ...services.ai_service import AIService
from ...utils.file_utils import save_uploaded_file, get_file_path
from ...config import settings

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(
    request: Request,
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, DOC, TXT)")
):
    """
    Upload and analyze resume file.
    This triggers the entire analysis pipeline:
    1. File upload and validation
    2. Resume parsing 
    3. Skills analysis by LLM
    4. Preparation for interview
    """
    try:
        # Get session ID from request
        session_id = getattr(request.state, 'session_id', str(uuid.uuid4()))
        session_data = get_session(session_id)
        
        # Validate uploaded file
        validated_file = await validate_file_upload(file)
        
        # Save file to disk
        file_path = await save_uploaded_file(validated_file, session_id)
        
        # Step 1: Parse resume content
        parser = ResumeParser()
        resume_data = await parser.parse_resume(file_path)
        
        if not resume_data or not resume_data.get('text'):
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from resume. Please check file format."
            )
        
        # Step 2: Analyze skills using LLM
        ai_service = AIService()
        skills_analysis = await ai_service.analyze_resume_skills(resume_data['text'])
        
        # Step 3: Store in session
        session_data.update({
            'resume_data': resume_data,
            'skills_analysis': skills_analysis,
            'file_path': file_path,
            'upload_time': datetime.now().isoformat()
        })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Resume uploaded and analyzed successfully!",
                "session_id": session_id,
                "data": {
                    "filename": validated_file.filename,
                    "skills_found": len(skills_analysis.get('skills', [])),
                    "experience_level": skills_analysis.get('experience_level', 'Not determined'),
                    "primary_skills": skills_analysis.get('primary_skills', [])[:5],  # Top 5
                    "analysis_summary": skills_analysis.get('summary', 'Analysis completed')
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/upload-status/{session_id}")
async def get_upload_status(session_id: str):
    """Check if resume has been uploaded and analyzed for a session."""
    try:
        session_data = get_session(session_id)
        
        has_resume = session_data.get('resume_data') is not None
        has_analysis = session_data.get('skills_analysis') is not None
        
        return {
            "session_id": session_id,
            "has_resume": has_resume,
            "has_analysis": has_analysis,
            "ready_for_interview": has_resume and has_analysis,
            "upload_time": session_data.get('upload_time'),
            "skills_count": len(session_data.get('skills_analysis', {}).get('skills', []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking upload status: {str(e)}"
        )


@router.delete("/clear-upload/{session_id}")
async def clear_upload(session_id: str):
    """Clear uploaded resume and start fresh."""
    try:
        session_data = get_session(session_id)
        
        # Delete uploaded file if exists
        if 'file_path' in session_data:
            file_path = session_data['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Clear session data
        session_data.clear()
        session_data.update({
            "resume_data": None,
            "skills_analysis": None,
            "questions": [],
            "responses": [],
            "current_question_index": 0,
            "interview_started": False,
            "interview_ended": False,
            "start_time": None,
            "end_time": None
        })
        
        return {
            "success": True,
            "message": "Upload cleared successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing upload: {str(e)}"
        )