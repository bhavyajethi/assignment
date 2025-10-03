import re
from typing import Dict, Any
from pathlib import Path

from ..config import settings


def validate_resume_file(filename: str, file_size: int) -> Dict[str, Any]:
    """Validate resume file upload - only checks file type, size, and security."""
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check filename exists
    if not filename or len(filename.strip()) == 0:
        validation_result["valid"] = False
        validation_result["errors"].append("Filename is required")
        return validation_result
    
    # Check file extension (only PDF, DOCX, DOC, TXT allowed)
    file_extension = Path(filename).suffix.lower().lstrip('.')
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        validation_result["valid"] = False
        validation_result["errors"].append(
            f"File type '.{file_extension}' not supported. "
            f"Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    if file_size > settings.MAX_FILE_SIZE:
        validation_result["valid"] = False
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        validation_result["errors"].append(
            f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds "
            f"maximum allowed size ({max_size_mb:.1f}MB)"
        )
    
    # Security check - prevent malicious file types
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar', '.app']
    if any(ext in filename.lower() for ext in dangerous_extensions):
        validation_result["valid"] = False
        validation_result["errors"].append("Potentially dangerous file type detected")
    
    # Warning for very small files
    if file_size < 1024:  # Less than 1KB
        validation_result["warnings"].append("File seems very small - ensure it contains resume content")
    
    return validation_result


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format."""
    if not session_id:
        return False
    
    # Check length
    if len(session_id) < 8 or len(session_id) > 50:
        return False
    
    # Check for valid characters (alphanumeric and hyphens only)
    if not re.match(r'^[a-zA-Z0-9\-]+$', session_id):
        return False
    
    return True


def validate_response_not_empty(response: str) -> Dict[str, Any]:
    """Basic validation to ensure response is not empty - AI will judge quality."""
    
    validation_result = {
        "valid": True,
        "errors": []
    }
    
    if not response or not response.strip():
        validation_result["valid"] = False
        validation_result["errors"].append("Response cannot be empty")
    
    return validation_result


def sanitize_user_input(user_input: str, max_length: int = 10000) -> str:
    """Sanitize user input for security - remove potentially harmful content."""
    
    if not user_input:
        return ""
    
    # Remove HTML/script tags for security
    sanitized = re.sub(r'<script.*?</script>', '', user_input, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Limit length to prevent abuse
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Clean up excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters."""
    
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Remove multiple underscores/spaces
    sanitized = re.sub(r'[_\s]+', '_', sanitized)
    
    # Ensure filename isn't too long (max 100 chars)
    if len(sanitized) > 100:
        name_part = Path(sanitized).stem[:80]
        extension = Path(sanitized).suffix
        sanitized = f"{name_part}{extension}"
    
    return sanitized


def validate_file_path_security(file_path: str, allowed_directories: list) -> bool:
    """Validate file path is within allowed directories for security."""
    
    try:
        file_path_obj = Path(file_path).resolve()
        
        # Check if path is within allowed directories
        for allowed_dir in allowed_directories:
            allowed_path = Path(allowed_dir).resolve()
            try:
                file_path_obj.relative_to(allowed_path)
                return True  # Path is within this allowed directory
            except ValueError:
                continue  # Try next allowed directory
        
        return False  # Path not in any allowed directory
        
    except Exception:
        return False


def check_suspicious_content(text: str) -> Dict[str, Any]:
    """Check for suspicious patterns in text for security monitoring (not blocking)."""
    
    result = {
        "suspicious": False,
        "warnings": []
    }
    
    # Check for potential sensitive information patterns
    patterns = {
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "ssn": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        "password_mention": r'\b(password|passwd|pwd)\s*[:=]\s*\S+',
    }
    
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            result["suspicious"] = True
            result["warnings"].append(f"Potential {pattern_name.replace('_', ' ')} detected")
    
    return result