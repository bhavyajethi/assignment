import os
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportGenerator:
    """Generates interview reports in PDF format."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """custom styles for report generation"""
        self.styles.add(ParagraphStyle(
            name="CustomTitle",
            parent=self.styles['Heading1'],
            fontsize=18,
            spaceAfter=30,
            textColor=colors.black
        ))

        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            parent=self.styles['Heading2'],
            fontsize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))

    async def create_report(self, session_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """create comprehensive report"""
        try:
            responses = session_data.get("responses",[])
            skills_analysis = session_data.get("skills_analysis",[])
            interview_duration = self._calculate_duration(session_data)

            report = {
                'report_id': f"report_{session_data.get('session_id', 'unknown')[:8]}",
                'generated_at': datetime.utcnow().isoformat(),
                'candidate_info': self._generate_candidate_section(session_data),
                'interview_summary': self._generate_summary_summary(session_data, interview_duration),
                'performance_analysis': self._generate_question_analysis(ai_analysis),
                'question_analysis': self._generate_question_analysis(responses, ai_analysis),
                'skills_assessment': self._generate_skills_assessment(skills_analysis, ai_analysis),
                'strength_weakness': self._generate_strengths.weaknesses(ai_analysis),
                'recommendatioons': self._generate_recommendations(ai_analysis),
                'overall_score': self._generate_overall_score(ai_analysis),
                'next_steps': self._generate_next_steps(ai_analysis)
            }
            return report
        except Exception as e:
            raise Exception(f"Error creating report: {str(e)}")

    def _generate_candidate_section(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """generate candidate information section"""

        resume_data = session_data.get("resume_data", {})
        skills_analysis = session_data.get("skills_analysis", [])

        return {
            'name': session_data.get('name', 'Candidate'),
            'email': session_data.get('email', 'Not Provided'),
            'phone': session_data.get('phone', 'Not Provided'),
            'experience_level': skills_analysis.get('experience_level', 'Not Determined'),
            'primary_domain': skills_analysis.get('primary_domain', 'Not Determined'),
            'total_skills_idetified': len(skills_analysis.get('skills', [])),
        }

    def _generate_interview_summary(self, session_data: Dict[str, Any], duration: str) -> Dict[str, Any]:
        """generate interview summary statistics"""

        responses = session_data.get("responses", [])
        questions = session_data.get("questions", [])

        return {
            'date': datetime.utcnow().strftime("%Y-%m-%d"),
            'duration': duration,
            'total_questions': len(questions),
            'questions_answered': len(responses),
            'completion_rate': f"{(len(responses) / len(questions) * 100):.1f}%" if questions else "0%",
            'average_response_length': self._calculate_average_response_length(responses),
            'interview_type': session_data.get('interview_preference', {}).get('interview_type', "General")
        }

    def _generate_performance_analysis(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """generate performance analysis section"""

        return {
            'overall_performance': ai_analysis.get('overall_performance', 'Good'),
            'communication_skills': ai_analysis.get('communication_score', 7),
            'technical_knowledge': ai_analysis.get('technical_score', 7),
            'problem_solving': ai_analysis.get('problem_solving_score', 7),
            'confidence_level': ai_analysis.get('confidence_score', 'Medium'),
            'response_quality': ai_analysis.get('response_quality', 'Satisfactory'),
            'areas_of_expertise': ai_analysis.get('expertise_areas', []),
            'performance_level': ai_analysis.get('performance_level', 'Intermediate')
        }

    def _generate_question_analysis(self, responses: List[Dict], ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """generate detailed question analysis section"""

        question_analysis = []
        response_analysis = ai_analysis.get('response_analysis', {})
        for i, response in enumerate(responses):
            analysis = response_analysis[i] if i < len(response_analysis) else {}

            question_analysis.append({
                'question_number': response.get('question_number', i + 1),
                'question': response.get('response',''),
                'question_type': response.get('response_type', 'general'),
                'response_summary': response.get('response', '')[:200] + "..." if len(response.get('response', '')) > 200 else response.get('response', ''),
                'score': analysis.get('score', 7),
                'feedback': analysis.get('feedback', 'Good response'),
                'strengths': analysis.get('strengths', []),
                'improvements': analysis.get('improvements', []),
                'time_taken': 'N/A'  # Would need timing implementation
            })
            return question_analysis

    def _generate_skills_assessment(self, skills_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """generate skills assessment section"""

        return {
            'techinical_skills':{
                'demonstrated': ai_analysis.get('demonstrated_technical_skills', []),
                'score': ai_analysis.get('technical_score', 7),
                'assessment': ai_analysis.get('technical_assessment', 'Adequate technical knowledge')
            },
            'soft_skills':{
                'demonstrated': ai_analysis.get('demonstrated_soft_skills', []),
                'score': ai_analysis.get('soft_skills_score', 7),
                'assessment': ai_analysis.get('soft_skills_assessment', 'Good communication and interpersonal skills')
            },
            'domain_expertise':{
                'primary_domain': skills_analysis.get('primary_domain', 'General'),
                'expertise_level': skills_analysis.get('domain_expertise_level', 'Intermediate'),
                'specific_knowledge': skills_analysis.get('specific_knowledge_areas', [])
            },
            'skill_gaps': ai_analysis.get('skill_gaps', []),
            'learning_recommendations': ai_analysis.get('learning_recommendations', [])
        }

    def _generate_strengths_weaknesses(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strengths and weaknesses analysis."""
        
        return {
            'key_strengths': ai_analysis.get('key_strengths', [
                'Good communication skills',
                'Problem-solving approach',
                'Technical understanding'
            ]),
            'areas_for_improvement': ai_analysis.get('improvement_areas', [
                'Could provide more specific examples',
                'Consider deepening technical knowledge',
                'Practice articulating complex concepts'
            ]),
            'standout_qualities': ai_analysis.get('standout_qualities', []),
            'potential_concerns': ai_analysis.get('concerns', [])
        }
    
    def _generate_recommendations(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations section."""
        
        return {
            'hiring_recommendation': ai_analysis.get('hiring_recommendation', 'Consider for next round'),
            'confidence_level': ai_analysis.get('recommendation_confidence', 'Medium'),
            'next_interview_focus': ai_analysis.get('next_interview_focus', []),
            'role_suitability': ai_analysis.get('role_suitability', 'Good fit'),
            'development_areas': ai_analysis.get('development_recommendations', []),
            'follow_up_questions': ai_analysis.get('suggested_followup_questions', [])
        }
    
    def _calculate_overall_score(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall interview score."""
        
        # Weighted scoring
        technical_score = ai_analysis.get('technical_score', 7)
        communication_score = ai_analysis.get('communication_score', 7)
        problem_solving_score = ai_analysis.get('problem_solving_score', 7)
        
        # Weights
        technical_weight = 0.4
        communication_weight = 0.3
        problem_solving_weight = 0.3
        
        overall_score = (
            technical_score * technical_weight +
            communication_score * communication_weight +
            problem_solving_score * problem_solving_weight
        )
        
        # Convert to grade
        if overall_score >= 8.5:
            grade = 'A'
            level = 'Excellent'
        elif overall_score >= 7.5:
            grade = 'B'
            level = 'Good'
        elif overall_score >= 6.5:
            grade = 'C'
            level = 'Satisfactory'
        elif overall_score >= 5.5:
            grade = 'D'
            level = 'Below Average'
        else:
            grade = 'F'
            level = 'Poor'
        
        return {
            'numerical_score': round(overall_score, 1),
            'grade': grade,
            'performance_level': level,
            'score_breakdown': {
                'technical': technical_score,
                'communication': communication_score,
                'problem_solving': problem_solving_score
            }
        }
    
    def _generate_next_steps(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate next steps and action items."""
        
        return {
            'immediate_actions': ai_analysis.get('immediate_actions', [
                'Review technical concepts mentioned',
                'Practice explaining complex topics clearly',
                'Prepare specific project examples'
            ]),
            'long_term_development': ai_analysis.get('long_term_development', [
                'Continue building technical skills',
                'Gain more hands-on project experience',
                'Improve communication and presentation skills'
            ]),
            'resources': ai_analysis.get('recommended_resources', [
                'Online courses for skill gaps',
                'Practice interview platforms',
                'Technical documentation and tutorials'
            ]),
            'timeline': '2-4 weeks for immediate improvements'
        }
    
    async def export_to_pdf(self, report_data: Dict[str, Any], session_data: Dict[str, Any], session_id: str) -> str:
        """Export report to PDF format."""
        
        try:
            # Create exports directory if it doesn't exist
            os.makedirs('data/exports', exist_ok=True)
            
            filename = f"data/exports/interview_report_{session_id[:8]}_{datetime.now().strftime('%Y%m%d')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Build PDF content
            story = []
            
            # Title
            title = Paragraph("Interview Performance Report", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Candidate Info
            candidate_info = report_data['candidate_info']
            story.append(Paragraph("Candidate Information", self.styles['SectionHeader']))
            story.append(Paragraph(f"Name: {candidate_info['name']}", self.styles['Normal']))
            story.append(Paragraph(f"Experience Level: {candidate_info['experience_level']}", self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Interview Summary
            summary = report_data['interview_summary']
            story.append(Paragraph("Interview Summary", self.styles['SectionHeader']))
            story.append(Paragraph(f"Date: {summary['date']}", self.styles['Normal']))
            story.append(Paragraph(f"Duration: {summary['duration']}", self.styles['Normal']))
            story.append(Paragraph(f"Questions Answered: {summary['questions_answered']}/{summary['total_questions']}", self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Overall Score
            score = report_data['overall_score']
            story.append(Paragraph("Overall Performance", self.styles['SectionHeader']))
            story.append(Paragraph(f"Score: {score['numerical_score']}/10 (Grade: {score['grade']})", self.styles['Normal']))
            story.append(Paragraph(f"Performance Level: {score['performance_level']}", self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error exporting PDF: {str(e)}")
    
    def _calculate_duration(self, session_data: Dict[str, Any]) -> str:
        """Calculate interview duration."""
        try:
            start_time = session_data.get('start_time')
            end_time = session_data.get('end_time')
            
            if start_time and end_time:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration = end - start
                minutes = int(duration.total_seconds() / 60)
                return f"{minutes} minutes"
            
            return "Duration not available"
        except Exception:
            return "Duration calculation error"
    
    def _calculate_avg_response_length(self, responses: List[Dict]) -> str:
        """Calculate average response length in words."""
        if not responses:
            return "0 words"
        
        total_words = 0
        for response in responses:
            response_text = response.get('response', '')
            total_words += len(response_text.split())
        
        avg_words = total_words // len(responses)
        return f"{avg_words} words"