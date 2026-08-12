from fastapi import FastAPI
import asyncio
import logging
from app.core.config import Settings
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_repository import SalesRepository
from app.services.embedding_service import EmbeddingService

from app.routers import products, customers

settings = Settings()
logger = logging.getLogger("uvicorn")

product_repo = ProductRepository(settings)
sales_repo = SalesRepository(settings)
embed_svc = EmbeddingService(settings)

app = FastAPI(
    title="Ferretería - Búsqueda Semántica",
    description="API para búsqueda semántica de productos y sugerencias de venta según historial de clientes.",
    version="1.0.0",
)
app.state.settings = settings
app.state.product_repo = product_repo
app.state.sales_repo = sales_repo
app.state.embed_svc = embed_svc
app.state.indexing_complete = False


@app.on_event("startup")
async def startup():
    logger.info("Starting application, loading data and indexing products...")
    app.state.indexing_complete = False

    async def _run_index():
        try:
            await asyncio.to_thread(product_repo.index_products, embed_svc)
        finally:
            app.state.indexing_complete = True

    asyncio.create_task(_run_index())


app.include_router(products.router)
app.include_router(customers.router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Verificar estado del servicio",
    description="Endpoint de salud para comprobar que la API está levantada y responde correctamente.",
    response_model=dict,
    responses={
        200: {"description": "Servicio disponible."},
    },
)
async def health():
    return {"status": "ok"}
