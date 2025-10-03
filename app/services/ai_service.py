import json
from typing import Dict, List, Any, Optional
from groq import Groq
from ..config import settings


class AIService:
    """AI service for all LLM interactions using Groq API (GPT OSS 120B)."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.max_tokens = 4000
        self.temperature = 0.3  # Lower for more consistent responses
    
    async def parse_resume_content(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume content using AI to extract structured information."""
        
        prompt = f"""
        Analyze this resume and extract structured information. Return a JSON response with the following structure:
        {{
            "name": "candidate name",
            "email": "email address",
            "phone": "phone number", 
            "location": "city, state/country",
            "summary": "professional summary",
            "experience": [
                {{
                    "company": "company name",
                    "title": "job title",
                    "duration": "start - end dates",
                    "description": "job description"
                }}
            ],
            "education": [
                {{
                    "institution": "school name",
                    "degree": "degree type",
                    "field": "field of study",
                    "year": "graduation year"
                }}
            ],
            "skills": ["list of skills mentioned"],
            "projects": [
                {{
                    "name": "project name",
                    "description": "project description",
                    "technologies": ["tech stack used"]
                }}
            ],
            "certifications": ["list of certifications"],
            "languages": ["programming/spoken languages"]
        }}
        
        Resume text:
        {resume_text}
        
        Extract all available information. If a field is not found, use null. Be thorough and accurate.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._extract_basic_info_fallback(resume_text)
        except Exception as e:
            raise Exception(f"AI resume parsing failed: {str(e)}")
    
    async def analyze_resume_skills(self, resume_text: str) -> Dict[str, Any]:
        """Comprehensive AI analysis of skills from resume."""
        
        prompt = f"""
        Analyze this resume and provide a comprehensive skills assessment. Return JSON with this structure:
        {{
            "skills": [
                {{
                    "name": "skill name",
                    "category": "technical/soft/tool/domain",
                    "proficiency": "beginner/intermediate/advanced/expert",
                    "evidence": "where mentioned in resume",
                    "years_experience": "estimated years if mentioned"
                }}
            ],
            "experience_level": "entry/junior/mid/senior/lead",
            "years_experience": "total years estimated",
            "primary_domain": "main field like frontend/backend/fullstack/data science/etc",
            "technical_skills": ["list of technical skills"],
            "soft_skills": ["list of soft skills"],
            "tools_technologies": ["list of tools and technologies"],
            "strengths": ["key strengths identified"],
            "skill_gaps": ["potential missing skills for the role"],
            "learning_recommendations": ["skills to learn next"],
            "confidence_score": "1-10 rating of overall skill confidence",
            "summary": "brief assessment summary",
            "focus_areas": ["areas to focus interview on"],
            "interview_level": "appropriate interview difficulty level"
        }}
        
        Resume text:
        {resume_text}
        
        Be thorough in your analysis. Consider both explicitly mentioned skills and implied skills from job descriptions and projects.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return self._fallback_skills_analysis()
    
    async def generate_interview_questions(
        self,
        skills_analysis: Dict[str, Any],
        experience_level: str,
        interview_type: str,
        question_count: int
    ) -> List[Dict[str, Any]]:
        """Generate personalized interview questions based on candidate's profile."""
        
        skills_summary = json.dumps(skills_analysis, indent=2)
        
        prompt = f"""
        Generate {question_count} personalized interview questions for this candidate based on their skills analysis.
        
        Candidate Profile:
        {skills_summary}
        
        Interview Type: {interview_type}
        Experience Level: {experience_level}
        
        Return JSON array of questions with this structure:
        [
            {{
                "question": "the interview question",
                "type": "technical/behavioral/situational/system_design",
                "difficulty": "easy/medium/hard",
                "skills_tested": ["list of skills this tests"],
                "expected_duration": "estimated time to answer",
                "followup_potential": "yes/no",
                "reasoning": "why this question is relevant for this candidate"
            }}
        ]
        
        Guidelines:
        - Questions should be specific to their actual skills and experience
        - Mix different question types appropriately
        - Start easier and progress to harder questions  
        - Include both technical and behavioral questions
        - Reference their specific technologies and projects when possible
        - Ensure questions are appropriate for their experience level
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            
            # Add metadata
            for i, question in enumerate(questions):
                question['question_number'] = i + 1
                question['generated_at'] = "ai_generated"
            
            return questions
            
        except Exception as e:
            return self._fallback_questions(question_count)
    
    async def generate_interview_greeting(
        self,
        skills_analysis: Dict[str, Any],
        interview_plan: Dict[str, Any] = None,
        candidate_name: str = None
    ) -> str:
        """Generate personalized AI interviewer greeting."""
        
        candidate_info = f"Candidate: {candidate_name or 'Candidate'}\n"
        skills_info = f"Primary Domain: {skills_analysis.get('primary_domain', 'General')}\n"
        skills_info += f"Experience Level: {skills_analysis.get('experience_level', 'Unknown')}\n"
        skills_info += f"Key Skills: {', '.join(skills_analysis.get('technical_skills', [])[:5])}"
        
        prompt = f"""
        You are an AI interviewer. Generate a warm, professional greeting for this candidate.
        
        {candidate_info}
        {skills_info}
        
        The greeting should:
        - Welcome them warmly
        - Mention you've reviewed their resume
        - Reference 1-2 of their key skills or experiences
        - Ask if they're ready to begin
        - Be encouraging and professional
        - Keep it concise (2-3 sentences)
        
        Don't use quotes or special formatting. Just return the greeting text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Hello {candidate_name or 'there'}! I've reviewed your resume and I'm excited to learn more about your experience. Are you ready to begin the interview?"
    
    async def create_interview_plan(
        self,
        skills_analysis: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create AI-driven interview plan."""
        
        skills_summary = json.dumps(skills_analysis, indent=2)
        prefs_summary = json.dumps(preferences, indent=2)
        
        prompt = f"""
        Create an interview plan for this candidate based on their skills and preferences.
        
        Skills Analysis:
        {skills_summary}
        
        Preferences:
        {prefs_summary}
        
        Return JSON with this structure:
        {{
            "interview_type": "technical/behavioral/mixed",
            "question_count": "recommended number of questions",
            "estimated_duration": "estimated time in minutes",
            "focus_areas": ["key areas to focus on"],
            "difficulty_progression": "how to progress difficulty",
            "question_distribution": {{
                "technical": "percentage",
                "behavioral": "percentage", 
                "situational": "percentage"
            }},
            "special_considerations": ["any special notes"],
            "success_criteria": ["what constitutes a good performance"]
        }}
        
        Base recommendations on their experience level and skills.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return self._fallback_interview_plan()
    
    async def analyze_candidate_response(
        self,
        question: Dict[str, Any],
        response: str,
        skills_context: Dict[str, Any],
        interview_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze candidate's response using AI."""
        
        question_info = json.dumps(question, indent=2)
        skills_info = json.dumps(skills_context, indent=2)
        
        prompt = f"""
        Analyze this candidate's response to an interview question.
        
        Question:
        {question_info}
        
        Candidate's Response:
        "{response}"
        
        Candidate's Skills Context:
        {skills_info}
        
        Provide analysis in JSON format:
        {{
            "score": "1-10 rating",
            "feedback": "detailed feedback on the response",
            "strengths": ["what they did well"],
            "weaknesses": ["areas for improvement"],
            "technical_accuracy": "if applicable, rate technical correctness",
            "communication_quality": "rate how well they communicated",
            "completeness": "how complete was the answer",
            "relevance": "how relevant to the question",
            "examples_used": "did they provide good examples",
            "needs_followup": "true/false - should we ask a follow-up",
            "followup_suggestion": "potential follow-up question if needed",
            "red_flags": ["any concerning aspects"],
            "positive_indicators": ["encouraging signs"],
            "overall_assessment": "brief overall assessment"
        }}
        
        Be fair but thorough in your evaluation.
        """
        
        try:
            response_analysis = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2
            )
            
            content = response_analysis.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return self._fallback_response_analysis(response)
    
    async def determine_next_interview_action(
        self,
        response_analysis: Dict[str, Any],
        current_progress: Dict[str, Any],
        remaining_questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """AI determines the next action in the interview."""
        
        analysis_summary = json.dumps(response_analysis, indent=2)
        progress_info = f"Questions answered: {len(current_progress.get('responses', []))}"
        progress_info += f"\nRemaining questions: {len(remaining_questions)}"
        
        prompt = f"""
        Based on the candidate's response analysis and interview progress, determine the next action.
        
        Response Analysis:
        {analysis_summary}
        
        Current Progress:
        {progress_info}
        
        Return JSON with this structure:
        {{
            "action": "next_question/followup_question/end_interview/adapt_difficulty",
            "reasoning": "why this action was chosen",
            "confidence": "high/medium/low",
            "followup_question": "if action is followup, provide the question",
            "difficulty_adjustment": "if adapting, specify easier/harder",
            "estimated_remaining_time": "time estimate",
            "special_instructions": "any special notes"
        }}
        
        Consider:
        - Quality of the current response
        - Whether follow-up would add value
        - Overall interview progress
        - Candidate's engagement level
        """
        
        try:
            decision = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            content = decision.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return {
                "action": "next_question",
                "reasoning": "AI analysis failed, proceeding with next question",
                "confidence": "low",
                "error": str(e)
            }
    
    async def should_continue_interview(
        self,
        responses: List[Dict[str, Any]],
        skills_analysis: Dict[str, Any],
        interview_progress: Dict[str, Any],
        time_elapsed: str
    ) -> Dict[str, Any]:
        """AI decides if interview should continue."""
        
        responses_summary = f"Total responses: {len(responses)}"
        if responses:
            responses_summary += f"\nRecent responses quality: {[r.get('score', 'N/A') for r in responses[-3:]]}"
        
        progress_summary = json.dumps(interview_progress, indent=2)
        
        prompt = f"""
        Determine if this interview should continue or end based on the current state.
        
        Responses Summary:
        {responses_summary}
        
        Interview Progress:
        {progress_summary}
        
        Time Elapsed: {time_elapsed}
        
        Skills Analysis Summary:
        Experience Level: {skills_analysis.get('experience_level', 'Unknown')}
        Primary Domain: {skills_analysis.get('primary_domain', 'General')}
        
        Return JSON:
        {{
            "should_continue": "true/false",
            "reasoning": "detailed reasoning for the decision",
            "confidence": "high/medium/low",
            "data_sufficiency": "sufficient/needs_more/excellent",
            "recommended_questions_remaining": "number if continuing",
            "end_message": "message if ending interview"
        }}
        
        Consider:
        - Have we gathered enough information for evaluation?
        - Is the candidate engaged and providing quality responses?
        - Time constraints (target ~30 minutes)
        - Minimum of 5-6 substantial responses needed
        """
        
        try:
            decision = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )
            
            content = decision.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return {
                "should_continue": len(responses) < 8,
                "reasoning": "Fallback decision based on response count",
                "confidence": "low",
                "error": str(e)
            }
    
    async def analyze_complete_interview(
        self,
        responses: List[Dict[str, Any]],
        skills_analysis: Dict[str, Any],
        interview_duration: str
    ) -> Dict[str, Any]:
        """Comprehensive AI analysis of the complete interview."""
        
        responses_text = ""
        for i, resp in enumerate(responses, 1):
            responses_text += f"Q{i}: {resp.get('question', 'N/A')}\n"
            responses_text += f"A{i}: {resp.get('response', 'N/A')}\n\n"
        
        skills_summary = json.dumps(skills_analysis, indent=2)
        
        prompt = f"""
        Analyze this complete interview and provide comprehensive feedback.
        
        Candidate Skills Analysis:
        {skills_summary}
        
        Interview Duration: {interview_duration}
        
        Questions and Responses:
        {responses_text}
        
        Provide detailed analysis in JSON format:
        {{
            "overall_performance": "excellent/good/satisfactory/needs_improvement/poor",
            "overall_score": "1-10 numeric score",
            "technical_score": "1-10 for technical skills",
            "communication_score": "1-10 for communication",
            "problem_solving_score": "1-10 for problem solving",
            "key_strengths": ["top 3-5 strengths demonstrated"],
            "improvement_areas": ["top 3-5 areas needing work"],
            "demonstrated_skills": ["skills clearly shown in interview"],
            "skill_gaps": ["important skills not demonstrated"],
            "response_quality_trend": "improving/declining/consistent",
            "standout_responses": ["which responses were particularly good"],
            "concerning_responses": ["responses that raised concerns"],
            "cultural_fit_indicators": ["signs of cultural fit"],
            "learning_agility": "assessment of ability to learn",
            "hiring_recommendation": "strong_yes/yes/maybe/no/strong_no",
            "recommendation_reasoning": "detailed reasoning for recommendation",
            "next_interview_suggestions": ["what to focus on in next round"],
            "development_priorities": ["key areas for growth"],
            "estimated_onboarding_time": "time estimate to become productive",
            "role_suitability": "percentage match for the role",
            "detailed_feedback": {{
                "technical_depth": "assessment of technical knowledge depth",
                "practical_experience": "assessment of hands-on experience", 
                "communication_style": "analysis of communication approach",
                "problem_approach": "how they approach problems",
                "teamwork_indicators": "signs of teamwork ability"
            }}
        }}
        
        Be thorough, fair, and constructive in your analysis.
        """
        
        try:
            analysis = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            content = analysis.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return self._fallback_interview_analysis()
    
    async def generate_followup_question(
        self,
        original_question: Dict[str, Any],
        response: str,
        skills_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI-driven follow-up question."""
        
        question_info = json.dumps(original_question, indent=2)
        
        prompt = f"""
        Generate a follow-up question based on the candidate's response.
        
        Original Question:
        {question_info}
        
        Candidate's Response:
        "{response}"
        
        Skills Context:
        Primary Domain: {skills_context.get('primary_domain', 'General')}
        Experience Level: {skills_context.get('experience_level', 'Unknown')}
        
        Generate a follow-up question that:
        - Digs deeper into their response
        - Tests specific aspects they mentioned
        - Clarifies any ambiguous points
        - Explores practical application
        
        Return JSON:
        {{
            "question": "the follow-up question",
            "type": "clarification/deep_dive/practical_application",
            "reasoning": "why this follow-up is valuable",
            "skills_tested": ["skills this tests"],
            "expected_duration": "time estimate"
        }}
        
        Only generate if a follow-up would add significant value.
        """
        
        try:
            followup = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.4
            )
            
            content = followup.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return None
    
    # Fallback methods for when AI fails
    def _extract_basic_info_fallback(self, resume_text: str) -> Dict[str, Any]:
        """Basic fallback if AI parsing fails."""
        return {
            "name": "Candidate",
            "email": None,
            "phone": None,
            "summary": "Resume parsing failed",
            "skills": ["Communication"],
            "experience": [],
            "education": []
        }
    
    def _fallback_skills_analysis(self) -> Dict[str, Any]:
        """Fallback skills analysis."""
        return {
            "skills": [{"name": "Communication", "category": "soft", "proficiency": "intermediate"}],
            "experience_level": "intermediate",
            "primary_domain": "general",
            "technical_skills": ["Problem Solving"],
            "soft_skills": ["Communication"],
            "summary": "Unable to analyze skills, proceeding with generic assessment"
        }
    
    def _fallback_questions(self, count: int) -> List[Dict[str, Any]]:
        """Fallback questions if AI generation fails."""
        base_questions = [
            {
                "question": "Tell me about yourself and your background.",
                "type": "general",
                "difficulty": "easy",
                "skills_tested": ["communication"],
                "expected_duration": "3 minutes"
            },
            {
                "question": "Describe a challenging project you worked on recently.",
                "type": "behavioral",
                "difficulty": "medium", 
                "skills_tested": ["problem solving"],
                "expected_duration": "4 minutes"
            },
            {
                "question": "How do you approach learning new technologies?",
                "type": "behavioral",
                "difficulty": "easy",
                "skills_tested": ["learning agility"],
                "expected_duration": "3 minutes"
            }
        ]
        
        return base_questions[:count] if count <= len(base_questions) else base_questions * (count // len(base_questions) + 1)
    
    def _fallback_interview_plan(self) -> Dict[str, Any]:
        """Fallback interview plan."""
        return {
            "interview_type": "mixed",
            "question_count": 8,
            "estimated_duration": "25-30 minutes",
            "focus_areas": ["communication", "problem solving", "technical knowledge"],
            "difficulty_progression": "start easy, build up gradually"
        }
    
    def _fallback_response_analysis(self, response: str) -> Dict[str, Any]:
        """Fallback response analysis."""
        score = 6 if len(response.split()) > 20 else 4
        return {
            "score": score,
            "feedback": "Response recorded and noted.",
            "strengths": ["Provided an answer"],
            "needs_followup": False,
            "overall_assessment": "Response received"
        }
    
    def _fallback_interview_analysis(self) -> Dict[str, Any]:
        """Fallback complete interview analysis."""
        return {
            "overall_performance": "satisfactory",
            "overall_score": 6,
            "technical_score": 6,
            "communication_score": 6,
            "problem_solving_score": 6,
            "key_strengths": ["Completed the interview", "Engaged with questions"],
            "improvement_areas": ["Could provide more detailed examples"],
            "hiring_recommendation": "maybe",
            "recommendation_reasoning": "Interview analysis was limited due to technical issues"
        }