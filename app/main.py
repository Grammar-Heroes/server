from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, gameplay, users, adaptive, inventory, adventure, knowledge
from app.core.config import settings
from app.utils.logger import setup_grammar_cache_logger
import logging


def create_app() -> FastAPI:
    """Initialize and configure the FastAPI app."""

    # Setup structured logging for grammar cache and other modules
    setup_grammar_cache_logger()
    logger = logging.getLogger("uvicorn")

    app = FastAPI(
        title="Grammar Heroes Backend",
        debug=settings.DEBUG,
        description="Backend API for Grammar Heroes – adaptive grammar learning game.",
        version="1.0.0",
    )

    # --- CORS setup ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # you can restrict this to your frontend domain later
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    app.include_router(auth.router)
    app.include_router(gameplay.router)
    app.include_router(users.router)
    app.include_router(adaptive.router)
    app.include_router(inventory.router)
    app.include_router(adventure.router)
    app.include_router(knowledge.router)

    # --- Events ---
    @app.on_event("startup")
    async def on_startup():
        logger.info("🚀 Grammar Heroes Backend started successfully.")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("🛑 Shutting down Grammar Heroes Backend.")

    # --- Health Check Endpoint ---
    @app.get("/", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": "grammar-heroes-backend"}

    return app


app = create_app()