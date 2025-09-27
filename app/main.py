from fastapi import FastAPI
from app.routers import auth, gameplay, users, progress, adaptive, inventory, adventure
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title="Grammar Heroes Backend", debug=settings.DEBUG)

    # routers
    app.include_router(auth.router)
    app.include_router(gameplay.router)
    app.include_router(users.router)
    app.include_router(progress.router)
    app.include_router(adaptive.router)
    app.include_router(inventory.router)
    app.include_router(adventure.router)

    @app.on_event("startup")
    async def startup():
        pass

    return app

app = create_app()