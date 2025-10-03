from typing import Dict, List, Any, Optional
from ..services.ai_service import AIService


class SkillAnalyzer:
    """AI-driven skill analysis that dynamically identifies and categorizes skills."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def analyze_skills_from_resume(self, resume_text: str, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze and categorize skills from resume text."""
        try:
            # Send resume to AI for complete skill analysis
            skills_analysis = await self.ai_service.analyze_resume_skills(resume_text)
            
            # Add additional context from resume data if available
            if resume_data:
                skills_analysis['candidate_info'] = {
                    'name': resume_data.get('name'),
                    'email': resume_data.get('email'),
                    'phone': resume_data.get('phone')
                }
            
            return skills_analysis
            
        except Exception as e:
            raise Exception(f"Error analyzing skills: {str(e)}")
    
    async def get_skill_details(self, skill_name: str, context: str) -> Dict[str, Any]:
        """Get AI analysis of a specific skill in context."""
        try:
            skill_details = await self.ai_service.analyze_specific_skill(skill_name, context)
            return skill_details
            
        except Exception as e:
            return {
                'skill': skill_name,
                'analysis': f'Error analyzing skill: {str(e)}',
                'proficiency': 'Unknown'
            }
    
    async def compare_skills_to_job(self, skills_analysis: Dict[str, Any], job_requirements: str) -> Dict[str, Any]:
        """Use AI to compare candidate skills against job requirements."""
        try:
            comparison = await self.ai_service.compare_skills_to_job(skills_analysis, job_requirements)
            return comparison
            
        except Exception as e:
            return {
                'match_percentage': 0,
                'analysis': f'Error comparing skills: {str(e)}',
                'recommendations': []
            }