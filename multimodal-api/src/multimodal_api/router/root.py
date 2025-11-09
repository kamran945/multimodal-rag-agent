from fastapi import APIRouter

from loguru import logger

from multimodal_api.config.config import get_settings

settings = get_settings()

logger = logger.bind(name="RootAPI")

router_root = APIRouter()


@router_root.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation
    """
    return {"message": "Welcome to Multimodal API. Visit /docs for documentation"}
