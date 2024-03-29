from fastapi import FastAPI

from app.config import settings
from app.speech.router import router as speech_router
from app.user.router import router as user_router


def create_app() -> FastAPI:
    """
    Create and return a FastAPI instance with the specified routes and settings.

    Returns:
        FastAPI: A FastAPI instance with the specified routes and settings.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url="/mockingjay.json" if settings.show_docs else None,
    )

    app.include_router(user_router, prefix="/users")  # TODO: consider removing prefix
    app.include_router(speech_router)

    @app.get("/_health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    return app
