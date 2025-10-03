import os
import uuid 
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from ..config import settings

async def save_upload_file(file: UploadFile, session_id: str) -> str:
    "save uploaded file and return file path"
    try:
        # file directory is created if it doesn't exist
        upload_dir = Path(settings.UPLOAD_FOLDER)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # generate unique filename
        timestamp = datetime.utcnow.strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        unique_filename = f"resume_{session_id[:8]}_{timestamp}{file_extension}"

        file_path = upload_dir/unique_filename

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        await file.seek(0)
        return str(file_path)
        
    except Exception as e:
        raise Exception(f"Failed to save uploaded file: {str(e)}")

def get_file_path(filename: str) -> str:
    "get full path for file in directory"
    return os.path.join(settings.UPLOAD_FOLDER, filename)

def validate_file_extension(filename: str) -> str:
    "validate file extension"
    if not filename:
        return False
    file_extension = Path(filename).suffix.lower().lstrip('.')
    return file_extension in settings.ALLOWED_EXTENSIONS

def get_file_size(file_path: str) -> int:
    "get file size in bytes"
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def generate_unique_fullname(original_filename: str, session_id: str=None) -> str:
    "generate unique file name with timestamp and session id"
    timestamp = datetime.utcnow.strftime("%Y%m%d_%H%M%S")
    file_stem = Path(original_filename).stem
    file_extension = Path(original_filename).suffix

    if session_id:
        session_part = session_id[:8]
        return f"{file_stem}_{session_part}_{timestamp}{file_extension}"
    else:
        unique_id = str(uuid.uuid4())[:8]
        return f"{file_stem}_{unique_id}_{timestamp}{file_extension}"

def cleanup_file(file_path: str) -> bool:
    "delete file"
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting the file{file_path}: {str(e)}")
        return False

def ensure_directory_exists(directory_path: str) -> bool:
    "ensure directory exists, create if not"
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {str(e)}")
        return False

def get_file_info(file_path: str) -> dict:
    "get detailed info about the file"
    try:
        if not os.path.exists(file_path):
            return {"exists": False}

        stat_info = os.stat(file_path)
        path_obj = Path(file_path)

        return {
            'exists': True,
            'filename': path_obj.name,
            'size_bytes': stat_info.st_size,
            'size_mb': round(stat_info.st_size / (1024*1024), 2),
            'extension': path_obj.suffix,
            'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        }
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def is_file_too_large(file_size: int, max_size: int = None) -> bool:
    """Check if file size exceeds maximum allowed size."""
    max_size = max_size or settings.MAX_FILE_SIZE
    return file_size > max_size


async def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """Read file content asynchronously."""
    try:
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            return await f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
            return await f.read()
    except Exception as e:
        raise Exception(f"Failed to read file {file_path}: {str(e)}")


def get_mime_type(file_path: str) -> str:
    """Get MIME type of file based on extension."""
    extension = Path(file_path).suffix.lower()
    
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.csv': 'text/csv'
    }
    
    return mime_types.get(extension, 'application/octet-stream')


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters."""
    import re
    
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Remove multiple underscores/spaces
    sanitized = re.sub(r'[_\s]+', '_', sanitized)
    
    # Ensure filename isn't too long
    if len(sanitized) > 100:
        name_part = Path(sanitized).stem[:80]
        extension = Path(sanitized).suffix
        sanitized = f"{name_part}{extension}"
    
    return sanitized


def create_backup_filename(original_path: str) -> str:
    """Create backup filename with timestamp."""
    path_obj = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{path_obj.stem}_backup_{timestamp}{path_obj.suffix}"