""""custom exceptions for the ai mock interviewer"""

from typing import Optional, Dict, Any

class MockInterviewException(Exception):
    """base exception for all ai mock errors"""
    def __init__(self, message: str, error_code: str=None, details: Dict[str, Any]=None):
        self.message = message
        self.error_code = error_code or "GENERAL ERROR"
        self.details = details or {}
        super().__init__(self.message)

class ResumeParsingException(MockInterviewException):
    """exception for failed resume parsing"""
    def __init__(self, message:str, file_path:str = None, file_type:str = None):
        super().__init__(
            message,
            error_code="RESUME_PARSING_ERROR",
            details={"file_path": file_path, "file_type": file_type}
        )

class AIServiceException(MockInterviewException):
    """exception for failed ai service operations"""
    def __init__(self, message:str, operation:str = None, ai_service:str = None):
        super().__init__(
            message,
            error_code="AI_SERVICE_ERROR",
            details={"operation": operation, "ai_service": ai_service}
        )

class SkillAnalysisException(MockInterviewException):
    """exception for failed skills analysis"""
    def __init__(self, message:str, resume_content_length:int = None):
        super().__init__(
            message,
            error_code="SKILL_ANALYSIS_ERROR",
            details={"resume_content_length": resume_content_length}
        )

class InterviewEnginerException(MockInterviewException):
    """exception raised during mock interview processing"""
    def __init__(self, message:str, session_id:str = None, current_question:int = None):
        super().__init__(
            message,
            error_code="INTERVIEW_ENGINE_ERROR",
            details={"session_id": session_id, "current_question": current_question}
        )

class QuestionGenerationException(MockInterviewException):
    """Exception raised when question generation fails."""
    
    def __init__(self, message: str, question_type: str = None, skills_context: str = None):
        super().__init__(
            message,
            error_code="QUESTION_GENERATION_ERROR",
            details={"question_type": question_type, "skills_context": skills_context}
        )

class ResponseAnalysisException(MockInterviewException):
    """exception raised when response analysis fails"""
    def __init__(self, message: str, reponse_length: int = None,question_type: str = None):
        super().__init__(
            message,
            error_code="RESPONSE_ANALYSIS_ERROR",
            details={"question_type": question_type, "skills_context": reponse_length}
        )

class ReportGeneratioException(MockInterviewException):
    """exception reised for report generation"""
    def __init__(self, message: str, report_type: str = None, data_available: bool = None):
        super().__init__(
            message,
            error_code="REPORT_GENERATION_ERROR",
            details={"report_type": report_type, "data_available": data_available}
        )

class FileUploadException(MockInterviewException):
    """exception raised for file upload errors"""
    def __init__(self, message: str, filename: str = None, file_size: int = None):
        super().__init__(
            message,
            error_code="FILE_UPLOAD_ERROR",
            details={"filename": filename, "file_size": file_size}
        )

class SessionManagementException(MockInterviewException):
    """exception raised during session management operations"""
    def __init__(self, message: str, session_id: str = None, operation: str = None):
        super().__init__(
            message,
            error_code="SESSION_MANAGEMENT_ERROR",
            details={"session_id": session_id, "operation": operation}
        )

class ValidationException(MockInterviewException):
    """exception raised for validation errors"""
    def __init__(self, message: str, field_name: str = None, validation_type: str = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field_name": field_name, "validation_type": validation_type}
        )

class StorageException(MockInterviewException):
    """exception raised during storage operations"""
    def __init__(self, message:str, operation: str = None, file_path: str = None):
        super.__init__(
            message,
            error_code = "STORAGE_ERROR",
            details = {"operation": operation, "file_path": file_path}
        )

class ConfigurationException(MockInterviewException):
    """Exception raised when configuration is invalid or missing."""
    def __init__(self, message: str, config_key: str = None, config_value: str = None):
        super.__init__(
            message,
            error_code = "STORAGE_ERROR",
            details = {"config_key": config_key, "config_value": config_value}
        )

class InterviewFlowException(MockInterviewException):
    """Exception raised when interview flow logic encounters an error"""
    def __init__(self, message: str, current_state: str = None, expected_state: str = None):
        super.__init__(
            message,
            error_code = "INTERVIEW_FLOW_ERROR",
            details = {"current_state": current_state, "expected_state": expected_state}
        )

# Exception handler utilities
def format_exception_response(exception: MockInterviewException) -> Dict[str, Any]:
    """Format exception for API response."""
    return {
        "error": True,
        "error_code": exception.error_code,
        "message": exception.message,
        "details": exception.details,
        "timestamp": str(Exception.__class__.__name__)
    }


def log_exception(exception: Exception, context: Dict[str, Any] = None) -> None:
    """Log exception with context for debugging."""
    import logging
    
    logger = logging.getLogger(__name__)
    
    error_info = {
        "exception_type": exception.__class__.__name__,
        "message": str(exception),
        "context": context or {}
    }
    
    if isinstance(exception, MockInterviewException):
        error_info.update({
            "error_code": exception.error_code,
            "details": exception.details
        })
    
    logger.error(f"Application Error: {error_info}")


def handle_ai_service_errors(func):
    """Decorator to handle AI service errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "api" in str(e).lower() or "groq" in str(e).lower():
                raise AIServiceException(
                    f"AI service error: {str(e)}",
                    operation=func.__name__
                )
            else:
                raise MockInterviewException(
                    f"Unexpected error in {func.__name__}: {str(e)}"
                )
    return wrapper


def handle_file_operations(func):
    """Decorator to handle file operation errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise StorageException(
                f"File not found: {str(e)}",
                operation=func.__name__
            )
        except PermissionError as e:
            raise StorageException(
                f"Permission denied: {str(e)}",
                operation=func.__name__
            )
        except Exception as e:
            raise StorageException(
                f"File operation failed: {str(e)}",
                operation=func.__name__
            )
    return wrapper


# Retry mechanism for transient errors
def with_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry operations that might fail transiently."""
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (AIServiceException, StorageException) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise e
                except Exception as e:
                    # Don't retry for other types of exceptions
                    raise e
            
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator