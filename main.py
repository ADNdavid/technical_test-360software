from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.core.config import Settings
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_repository import SalesRepository
from app.services.embedding_service import EmbeddingService

from app.routers import products, customers

settings = Settings()

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application, loading data and indexing products...")
    product_repo = ProductRepository(settings)
    sales_repo = SalesRepository(settings)
    embed_svc = EmbeddingService(settings)

    # Index products embeddings at startup
    # Launch indexing in a background task so startup isn't blocked
    import asyncio

    app.state.indexing_complete = False

    async def _run_index():
        try:
            await asyncio.to_thread(product_repo.index_products, embed_svc)
        finally:
            app.state.indexing_complete = True

    asyncio.create_task(_run_index())

    app.state.settings = settings
    app.state.product_repo = product_repo
    app.state.sales_repo = sales_repo
    app.state.embed_svc = embed_svc

    yield

    logger.info("Shutting down application")


app = FastAPI(lifespan=lifespan, title="Ferretería - Búsqueda Semántica")
app.include_router(products.router)
app.include_router(customers.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
