# backend/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key for protected endpoints."""
    if api_key != get_settings().SAMBANOVA_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

def get_services():
    """Dependency for accessing global services."""
    from app.main import services
    return services