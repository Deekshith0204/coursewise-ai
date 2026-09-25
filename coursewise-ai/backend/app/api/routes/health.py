from fastapi import APIRouter
from ...schemas.schemas import HealthResponse
from ...services.ai_service import ai_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_health():
    config = ai_service.get_config_info()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        app_name="CourseWise AI",
        ai_configured=config["configured"],
        ai_provider=config["provider"],
        ai_model=config["model"]
    )


@router.get("/config")
def get_config():
    return ai_service.get_config_info()
