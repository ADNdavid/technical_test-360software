from typing import List, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

router = APIRouter(prefix="/products", tags=["Products"])


class ProductSearchRequest(BaseModel):
    """Request payload for semantic product search."""

    query: str = Field(
        ...,
        min_length=3,
        description="Texto de búsqueda del producto que se desea localizar semánticamente.",
        examples=["tuerca de 1/2", "caja de tornillos 5mm"],
    )

    @field_validator("query")
    @classmethod
    def strip_query(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("query no puede estar vacío")
        return value


class ProductMatch(BaseModel):
    """Item devuelto por la búsqueda semántica."""

    product_id: str = Field(..., description="Identificador del producto.")
    description: str = Field(..., description="Descripción del producto.")
    category: str = Field(..., description="Categoría o nombre del producto relacionado.")
    similarity: float = Field(..., description="Puntaje combinado de similitud semántica y texto.")
    semantic_similarity: float = Field(..., description="Similitud semántica calculada por el modelo de embeddings.")
    text_match: float = Field(..., description="Coincidencia con términos del texto de la consulta.")


class ProductSearchResponse(BaseModel):
    """Respuesta de búsqueda de productos."""

    query: str = Field(..., description="Consulta original normalizada enviada por el cliente.")
    results: List[ProductMatch] = Field(..., description="Listado ordenado por mayor similitud.")


@router.post(
    '/search',
    response_model=ProductSearchResponse,
    summary="Buscar productos por texto",
    description="Busca productos usando embeddings semánticos y una coincidencia textual ligera para ordenar los resultados.",
    responses={
        200: {"description": "Búsqueda realizada correctamente."},
        400: {"description": "La consulta no es válida."},
        503: {"description": "El servicio de búsqueda no está disponible."},
    },
)
async def search_products(req: ProductSearchRequest, request: Request):
    product_repo = request.app.state.product_repo
    embed_svc = request.app.state.embed_svc
    settings = request.app.state.settings

    if product_repo is None or embed_svc is None:
        raise HTTPException(status_code=503, detail="Search service unavailable")

    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")

    q_emb = embed_svc.embed_text(req.query)
    results = product_repo.top_k_similar(q_emb, req.query, k=settings.TOP_K)
    for r in results:
        r['similarity'] = round(r['similarity'], 4)
        r['semantic_similarity'] = round(r.get('semantic_similarity', 0.0), 4)
        r['text_match'] = round(r.get('text_match', 0.0), 4)
    return {"query": req.query, "results": results}
