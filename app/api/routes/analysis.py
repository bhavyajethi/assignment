from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from ...dependencies import get_session
from ...services.ai_service import AIService
from ...core.skill_analyzer import SkillAnalyzer

router = APIRouter()

@router.get("/skills-analysis/{session_id}")
async def get_skills_analysis(session_id: str):
    """Get detailed skills analysis from uploaded resume."""
    try:
        session_data = get_session(session_id)
        
        if not session_data.get('skills_analysis'):
            raise HTTPException(
                status_code=404,
                detail="No skills analysis found. Please upload a resume first."
            )
        
        skills_analysis = session_data['skills_analysis']
        
        return {
            "session_id": session_id,
            "analysis": skills_analysis,
            "summary": {
                "total_skills": len(skills_analysis.get('skills', [])),
                "experience_level": skills_analysis.get('experience_level'),
                "primary_domain": skills_analysis.get('primary_domain'),
                "years_experience": skills_analysis.get('years_experience', 'Not specified')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving skills analysis: {str(e)}"
        )


@router.post("/reanalyze-skills/{session_id}")
async def reanalyze_skills(session_id: str):
    """Re-run skills analysis on existing resume."""
    try:
        session_data = get_session(session_id)
        
        resume_data = session_data.get('resume_data')
        if not resume_data or not resume_data.get('text'):
            raise HTTPException(
                status_code=404,
                detail="No resume data found. Please upload a resume first."
            )
        
        # Re-analyze with AI service
        ai_service = AIService()
        new_analysis = await ai_service.analyze_resume_skills(resume_data['text'])
        
        # Update session
        session_data['skills_analysis'] = new_analysis
        
        return {
            "success": True,
            "message": "Skills re-analyzed successfully",
            "session_id": session_id,
            "analysis": new_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error re-analyzing skills: {str(e)}"
        )


@router.get("/analysis-summary/{session_id}")
async def get_analysis_summary(session_id: str):
    """Get a concise summary of the resume analysis."""
    try:
        session_data = get_session(session_id)
        
        skills_analysis = session_data.get('skills_analysis')
        if not skills_analysis:
            raise HTTPException(
                status_code=404,
                detail="No analysis found. Please upload and analyze a resume first."
            )
        
        # Create summary
        summary = {
            "candidate_profile": {
                "experience_level": skills_analysis.get('experience_level', 'Unknown'),
                "primary_domain": skills_analysis.get('primary_domain', 'General'),
                "years_experience": skills_analysis.get('years_experience', 'Not specified')
            },
            "skills_breakdown": {
                "technical_skills": skills_analysis.get('technical_skills', [])[:8],
                "soft_skills": skills_analysis.get('soft_skills', [])[:5],
                "tools_technologies": skills_analysis.get('tools_technologies', [])[:8]
            },
            "interview_readiness": {
                "recommended_focus_areas": skills_analysis.get('focus_areas', []),
                "estimated_interview_level": skills_analysis.get('interview_level', 'Intermediate'),
                "confidence_score": skills_analysis.get('confidence_score', 75)
            }
        }
        
        return {
            "session_id": session_id,
            "summary": summary,
            "ready_for_interview": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analysis summary: {str(e)}"
        )


@router.get("/skill-details/{session_id}/{skill_name}")
async def get_skill_details(session_id: str, skill_name: str):
    """Get detailed information about a specific skill."""
    try:
        session_data = get_session(session_id)
        
        skills_analysis = session_data.get('skills_analysis')
        if not skills_analysis:
            raise HTTPException(
                status_code=404,
                detail="No analysis found."
            )
        
        # Find skill in analysis
        all_skills = skills_analysis.get('skills', [])
        skill_info = None
        
        for skill in all_skills:
            if isinstance(skill, dict) and skill.get('name', '').lower() == skill_name.lower():
                skill_info = skill
                break
            elif isinstance(skill, str) and skill.lower() == skill_name.lower():
                skill_info = {"name": skill, "level": "Mentioned"}
                break
        
        if not skill_info:
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_name}' not found in analysis."
            )
        
        return {
            "session_id": session_id,
            "skill": skill_info,
            "related_questions": f"Questions about {skill_name} will be included in the interview"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving skill details: {str(e)}"
        )