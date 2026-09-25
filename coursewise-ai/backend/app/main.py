import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from .database.session import init_db
from .api.routes import health, documents, summaries, concepts, prerequisites

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("coursewise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown logic if any
    logger.info("CourseWise AI Backend shutting down.")


app = FastAPI(
    title="CourseWise AI Backend API",
    description="AI-Based Personalized Course Content Summarizer for Dense Technical Material",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again or check server logs."}
    )


# Mount routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(summaries.router, prefix="/api")
app.include_router(concepts.router, prefix="/api")
app.include_router(prerequisites.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to CourseWise AI API",
        "documentation": "/docs",
        "health": "/api/health"
    }
