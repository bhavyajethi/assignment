from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import os
from typing import Dict, Any

from ...dependencies import get_session
from ...core.report_generator import ReportGenerator
from ...services.ai_service import AIService
from ...config import settings

router = APIRouter()

@router.post("/generate-report/{session_id}")
async def generate_interview_report(session_id: str):
    """
    Generate comprehensive interview report after interview completion.
    Analyzes all responses and provides detailed feedback.
    """
    try:
        session_data = get_session(session_id)
        
        # Verify interview is completed
        if not session_data.get('interview_ended'):
            raise HTTPException(
                status_code=400,
                detail="Interview not completed yet. Cannot generate report."
            )
        
        responses = session_data.get('responses', [])
        if not responses:
            raise HTTPException(
                status_code=400,
                detail="No responses found to analyze."
            )
        
        # Generate report using AI service
        ai_service = AIService()
        report_generator = ReportGenerator()
        
        # AI analyzes all responses together for comprehensive feedback
        comprehensive_analysis = await ai_service.analyze_complete_interview(
            responses=responses,
            skills_analysis=session_data['skills_analysis'],
            interview_duration=_calculate_duration(session_data)
        )
        
        # Generate structured report
        report_data = await report_generator.create_report(
            session_data=session_data,
            ai_analysis=comprehensive_analysis
        )
        
        # Store report in session
        session_data['report'] = report_data
        session_data['report_generated_at'] = datetime.now().isoformat()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Interview report generated successfully!",
            "report": report_data,
            "generation_time": session_data['report_generated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )


@router.get("/report/{session_id}")
async def get_interview_report(session_id: str):
    """Get the generated interview report."""
    try:
        session_data = get_session(session_id)
        
        report = session_data.get('report')
        if not report:
            raise HTTPException(
                status_code=404,
                detail="No report found. Please generate report first."
            )
        
        return {
            "session_id": session_id,
            "report": report,
            "generated_at": session_data.get('report_generated_at'),
            "interview_completed_at": session_data.get('end_time')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report: {str(e)}"
        )


@router.get("/report-summary/{session_id}")
async def get_report_summary(session_id: str):
    """Get a quick summary of the interview performance."""
    try:
        session_data = get_session(session_id)
        
        report = session_data.get('report')
        if not report:
            raise HTTPException(
                status_code=404,
                detail="No report available."
            )
        
        # Extract key metrics for quick view
        summary = {
            "overall_score": report.get('overall_score', 0),
            "performance_level": report.get('performance_level', 'Unknown'),
            "strengths": report.get('key_strengths', [])[:3],  # Top 3
            "improvement_areas": report.get('improvement_areas', [])[:3],  # Top 3
            "recommendation": report.get('overall_recommendation', ''),
            "interview_stats": {
                "questions_answered": len(session_data.get('responses', [])),
                "duration": _calculate_duration(session_data),
                "completion_rate": "100%"  # Since report exists, interview was completed
            }
        }
        
        return {
            "session_id": session_id,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report summary: {str(e)}"
        )


@router.get("/export-report/{session_id}")
async def export_report_pdf(session_id: str):
    """Export interview report as PDF file."""
    try:
        session_data = get_session(session_id)
        
        report = session_data.get('report')
        if not report:
            raise HTTPException(
                status_code=404,
                detail="No report available to export."
            )
        
        # Generate PDF using report generator
        report_generator = ReportGenerator()
        pdf_path = await report_generator.export_to_pdf(
            report_data=report,
            session_data=session_data,
            session_id=session_id
        )
        
        # Return file response
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"interview_report_{session_id[:8]}.pdf",
            headers={"Content-Disposition": f"attachment; filename=interview_report_{session_id[:8]}.pdf"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting report: {str(e)}"
        )


@router.get("/detailed-feedback/{session_id}")
async def get_detailed_feedback(session_id: str):
    """Get detailed question-by-question feedback."""
    try:
        session_data = get_session(session_id)
        
        report = session_data.get('report')
        if not report:
            raise HTTPException(
                status_code=404,
                detail="No report available."
            )
        
        # Get question-by-question analysis
        detailed_feedback = report.get('question_analysis', [])
        
        return {
            "session_id": session_id,
            "total_questions": len(detailed_feedback),
            "detailed_feedback": detailed_feedback,
            "overall_patterns": report.get('response_patterns', {}),
            "recommendations": report.get('specific_recommendations', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving detailed feedback: {str(e)}"
        )


@router.delete("/clear-report/{session_id}")
async def clear_report(session_id: str):
    """Clear generated report (for re-generation or cleanup)."""
    try:
        session_data = get_session(session_id)
        
        # Remove report data
        if 'report' in session_data:
            del session_data['report']
        if 'report_generated_at' in session_data:
            del session_data['report_generated_at']
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Report cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing report: {str(e)}"
        )


def _calculate_duration(session_data: Dict[str, Any]) -> str:
    """Helper function to calculate interview duration."""
    try:
        start_time = session_data.get('start_time')
        end_time = session_data.get('end_time')
        
        if not start_time or not end_time:
            return "Duration not available"
        
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        
        duration = end - start
        total_minutes = int(duration.total_seconds() / 60)
        
        if total_minutes < 1:
            return "Less than 1 minute"
        elif total_minutes == 1:
            return "1 minute"
        else:
            return f"{total_minutes} minutes"
            
    except Exception:
        return "Duration calculation error"