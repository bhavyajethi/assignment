import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import aiofiles
from pathlib import Path

from ..config import settings


class StorageService:
    """Handles file storage, session data persistence, and cleanup operations."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_FOLDER)
        self.exports_dir = Path("data/exports")
        self.sessions_dir = Path("data/sessions")
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        for directory in [self.upload_dir, self.exports_dir, self.sessions_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def save_uploaded_file(self, file, session_id: str) -> str:
        """Save uploaded resume file to storage."""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = file.filename
            file_extension = Path(original_filename).suffix
            
            new_filename = f"resume_{session_id[:8]}_{timestamp}{file_extension}"
            file_path = self.upload_dir / new_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return str(file_path)
            
        except Exception as e:
            raise Exception(f"Failed to save uploaded file: {str(e)}")
    
    async def save_session_data(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session data to persistent storage."""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            
            # Add metadata
            session_data_with_meta = {
                "session_id": session_id,
                "last_updated": datetime.now().isoformat(),
                "data": session_data
            }
            
            async with aiofiles.open(session_file, 'w') as f:
                await f.write(json.dumps(session_data_with_meta, indent=2, default=str))
            
            return True
            
        except Exception as e:
            print(f"Failed to save session data: {str(e)}")
            return False
    
    async def load_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from persistent storage."""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            async with aiofiles.open(session_file, 'r') as f:
                content = await f.read()
                session_info = json.loads(content)
            
            return session_info.get('data', {})
            
        except Exception as e:
            print(f"Failed to load session data: {str(e)}")
            return None
    
    async def delete_session_data(self, session_id: str) -> bool:
        """Delete session data and associated files."""
        try:
            # Delete session file
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            # Delete associated uploaded files
            await self.cleanup_session_files(session_id)
            
            return True
            
        except Exception as e:
            print(f"Failed to delete session data: {str(e)}")
            return False
    
    async def save_report_file(self, report_data: Dict[str, Any], session_id: str, format: str = "json") -> str:
        """Save interview report to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "json":
                filename = f"report_{session_id[:8]}_{timestamp}.json"
                filepath = self.exports_dir / filename
                
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(json.dumps(report_data, indent=2, default=str))
                    
            elif format.lower() == "txt":
                filename = f"report_{session_id[:8]}_{timestamp}.txt"
                filepath = self.exports_dir / filename
                
                report_text = self._format_report_as_text(report_data)
                async with aiofiles.open(filepath, 'w') as f:
                    await f.write(report_text)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Failed to save report: {str(e)}")
    
    def _format_report_as_text(self, report_data: Dict[str, Any]) -> str:
        """Format report data as readable text."""
        
        text = "=== INTERVIEW PERFORMANCE REPORT ===\n\n"
        
        # Candidate info
        if 'candidate_info' in report_data:
            candidate = report_data['candidate_info']
            text += f"Candidate: {candidate.get('name', 'N/A')}\n"
            text += f"Email: {candidate.get('email', 'N/A')}\n"
            text += f"Experience Level: {candidate.get('experience_level', 'N/A')}\n\n"
        
        # Interview summary
        if 'interview_summary' in report_data:
            summary = report_data['interview_summary']
            text += "INTERVIEW SUMMARY\n"
            text += "-" * 20 + "\n"
            text += f"Date: {summary.get('date', 'N/A')}\n"
            text += f"Duration: {summary.get('duration', 'N/A')}\n"
            text += f"Questions Answered: {summary.get('questions_answered', 'N/A')}\n"
            text += f"Completion Rate: {summary.get('completion_rate', 'N/A')}\n\n"
        
        # Overall score
        if 'overall_score' in report_data:
            score = report_data['overall_score']
            text += "OVERALL PERFORMANCE\n"
            text += "-" * 20 + "\n"
            text += f"Score: {score.get('numerical_score', 'N/A')}/10\n"
            text += f"Grade: {score.get('grade', 'N/A')}\n"
            text += f"Performance Level: {score.get('performance_level', 'N/A')}\n\n"
        
        # Strengths and weaknesses
        if 'strengths_weaknesses' in report_data:
            sw = report_data['strengths_weaknesses']
            text += "KEY STRENGTHS\n"
            text += "-" * 15 + "\n"
            for strength in sw.get('key_strengths', []):
                text += f"• {strength}\n"
            text += "\n"
            
            text += "AREAS FOR IMPROVEMENT\n"
            text += "-" * 25 + "\n"
            for area in sw.get('areas_for_improvement', []):
                text += f"• {area}\n"
            text += "\n"
        
        # Recommendations
        if 'recommendations' in report_data:
            rec = report_data['recommendations']
            text += "RECOMMENDATIONS\n"
            text += "-" * 17 + "\n"
            text += f"Hiring Recommendation: {rec.get('hiring_recommendation', 'N/A')}\n"
            text += f"Role Suitability: {rec.get('role_suitability', 'N/A')}\n\n"
        
        return text
    
    async def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get information about a stored file."""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            return {
                "exists": True,
                "filename": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    async def cleanup_old_files(self, days_old: int = 7) -> Dict[str, int]:
        """Clean up old files and sessions."""
        
        cleanup_stats = {
            "uploads_deleted": 0,
            "sessions_deleted": 0,
            "reports_deleted": 0,
            "errors": 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            # Clean up old uploads
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_modified < cutoff_date:
                        file_path.unlink()
                        cleanup_stats["uploads_deleted"] += 1
            
            # Clean up old session files
            for file_path in self.sessions_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.json':
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_modified < cutoff_date:
                        file_path.unlink()
                        cleanup_stats["sessions_deleted"] += 1
            
            # Clean up old reports
            for file_path in self.exports_dir.iterdir():
                if file_path.is_file():
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_modified < cutoff_date:
                        file_path.unlink()
                        cleanup_stats["reports_deleted"] += 1
                        
        except Exception as e:
            cleanup_stats["errors"] += 1
            print(f"Cleanup error: {str(e)}")
        
        return cleanup_stats
    
    async def cleanup_session_files(self, session_id: str) -> bool:
        """Clean up all files associated with a session."""
        try:
            session_prefix = session_id[:8]
            
            # Clean upload directory
            for file_path in self.upload_dir.iterdir():
                if session_prefix in file_path.name:
                    file_path.unlink()
            
            # Clean exports directory
            for file_path in self.exports_dir.iterdir():
                if session_prefix in file_path.name:
                    file_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"Failed to cleanup session files: {str(e)}")
            return False
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            stats = {
                "upload_directory": {
                    "path": str(self.upload_dir),
                    "file_count": 0,
                    "total_size_mb": 0
                },
                "sessions_directory": {
                    "path": str(self.sessions_dir),
                    "file_count": 0,
                    "total_size_mb": 0
                },
                "exports_directory": {
                    "path": str(self.exports_dir),
                    "file_count": 0,
                    "total_size_mb": 0
                }
            }
            
            # Calculate upload directory stats
            if self.upload_dir.exists():
                upload_files = list(self.upload_dir.iterdir())
                stats["upload_directory"]["file_count"] = len(upload_files)
                total_size = sum(f.stat().st_size for f in upload_files if f.is_file())
                stats["upload_directory"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Calculate sessions directory stats
            if self.sessions_dir.exists():
                session_files = list(self.sessions_dir.iterdir())
                stats["sessions_directory"]["file_count"] = len(session_files)
                total_size = sum(f.stat().st_size for f in session_files if f.is_file())
                stats["sessions_directory"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Calculate exports directory stats
            if self.exports_dir.exists():
                export_files = list(self.exports_dir.iterdir())
                stats["exports_directory"]["file_count"] = len(export_files)
                total_size = sum(f.stat().st_size for f in export_files if f.is_file())
                stats["exports_directory"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get storage stats: {str(e)}"}
    
    async def backup_session(self, session_id: str, backup_location: str = None) -> str:
        """Create a backup of session data and files."""
        try:
            if not backup_location:
                backup_location = "data/backups"
            
            backup_dir = Path(backup_location)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_backup_dir = backup_dir / f"session_{session_id[:8]}_{timestamp}"
            session_backup_dir.mkdir(exist_ok=True)
            
            # Copy session data file
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                shutil.copy2(session_file, session_backup_dir / "session_data.json")
            
            # Copy associated files
            session_prefix = session_id[:8]
            
            # Copy uploaded files
            upload_backup_dir = session_backup_dir / "uploads"
            upload_backup_dir.mkdir(exist_ok=True)
            for file_path in self.upload_dir.iterdir():
                if session_prefix in file_path.name:
                    shutil.copy2(file_path, upload_backup_dir / file_path.name)
            
            # Copy exported reports
            exports_backup_dir = session_backup_dir / "exports"
            exports_backup_dir.mkdir(exist_ok=True)
            for file_path in self.exports_dir.iterdir():
                if session_prefix in file_path.name:
                    shutil.copy2(file_path, exports_backup_dir / file_path.name)
            
            return str(session_backup_dir)
            
        except Exception as e:
            raise Exception(f"Failed to backup session: {str(e)}")
    
    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent interview sessions."""
        try:
            sessions = []
            session_files = sorted(
                self.sessions_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            for session_file in session_files[:limit]:
                try:
                    async with aiofiles.open(session_file, 'r') as f:
                        content = await f.read()
                        session_info = json.loads(content)
                    
                    session_summary = {
                        "session_id": session_info.get("session_id"),
                        "last_updated": session_info.get("last_updated"),
                        "candidate_name": session_info.get("data", {}).get("resume_data", {}).get("name", "Unknown"),
                        "interview_completed": session_info.get("data", {}).get("interview_ended", False),
                        "questions_answered": len(session_info.get("data", {}).get("responses", [])),
                        "file_size_kb": round(session_file.stat().st_size / 1024, 2)
                    }
                    sessions.append(session_summary)
                    
                except Exception as e:
                    print(f"Error reading session file {session_file}: {str(e)}")
                    continue
            
            return sessions
            
        except Exception as e:
            return []
    
    def get_upload_path(self, filename: str) -> str:
        """Get the full path for an uploaded file."""
        return str(self.upload_dir / filename)
    
    def get_export_path(self, filename: str) -> str:
        """Get the full path for an export file."""
        return str(self.exports_dir / filename)
    
    async def validate_file_access(self, filepath: str, session_id: str = None) -> bool:
        """Validate that a file can be accessed (security check)."""
        try:
            path = Path(filepath)
            
            # Check if file exists
            if not path.exists():
                return False
            
            # Check if file is in allowed directories
            allowed_dirs = [self.upload_dir, self.exports_dir, self.sessions_dir]
            if not any(str(path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
                return False
            
            # If session_id provided, check if file belongs to session
            if session_id:
                session_prefix = session_id[:8]
                if session_prefix not in path.name and session_id not in path.name:
                    return False
            
            return True
            
        except Exception:
            return False