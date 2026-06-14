from fastapi import APIRouter

router = APIRouter(tags=["infrastructure"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "immigration-navigator",
        "version": "0.1.0",
    }