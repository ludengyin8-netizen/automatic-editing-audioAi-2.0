"""VoiceFlow-CN Main Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.api import routes
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="VoiceFlow-CN API",
    description="AI-driven Chinese voiceover post-processing system",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup():
    """Initialize application on startup"""
    logger.info("Starting VoiceFlow-CN API...")
    init_db()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down VoiceFlow-CN API")

# Include routers
app.include_router(routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "VoiceFlow-CN",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
