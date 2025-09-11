from fastapi import FastAPI
from app.routers import auth, gameplay
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title="Grammar Heroes Backend", debug=settings.DEBUG)

    # routers
    app.include_router(auth.router)
    app.include_router(gameplay.router)

    @app.on_event("startup")
    async def startup():
        pass

    return app

app = create_app()