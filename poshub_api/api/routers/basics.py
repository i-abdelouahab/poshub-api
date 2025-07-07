from fastapi import APIRouter, status

router = APIRouter(tags=["basics"])


# Basic routes
@router.get("/", include_in_schema=False)
async def root():
    return {"message": "Poshub API Service"}


@router.get("/health", tags=["health"], status_code=status.HTTP_200_OK)
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
