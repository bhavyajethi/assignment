from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

from .config import settings
from .api.routes import upload, interview, analysis, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📁 Upload folder: {settings.UPLOAD_FOLDER}")
    yield
    # Shutdown
    print("👋 Shutting down AI Mock Interviewer")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered mock interview system with resume analysis",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(interview.router, prefix="/api", tags=["interview"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(report.router, prefix="/api", tags=["reports"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - mock interview landing."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "app_name": settings.APP_NAME}
    )


@app.get("/mock-interview", response_class=HTMLResponse)
async def mock_interview_page(request: Request):
    """Mock interview main page."""
    return templates.TemplateResponse(
        "upload.html", 
        {"request": request}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )