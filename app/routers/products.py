from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Any
import numpy as np

router = APIRouter(prefix="/products", tags=["Products"])

class ProductSearchRequest(BaseModel):
    query: str = Field(..., min_length=3)

    @validator('query')
    def strip_query(cls, v):
        return v.strip()


@router.post('/search')
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
    # round similarity
    for r in results:
        r['similarity'] = round(r['similarity'], 4)
        r['semantic_similarity'] = round(r.get('semantic_similarity', 0.0), 4)
        r['text_match'] = round(r.get('text_match', 0.0), 4)
    return {"query": req.query, "results": results}
