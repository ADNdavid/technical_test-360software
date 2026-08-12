from typing import List

from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/customers", tags=["Customers"])


class SuggestedProduct(BaseModel):
    """Producto sugerido para un cliente."""

    product_id: str = Field(..., description="Identificador del producto sugerido.")
    product_name: str = Field(..., description="Nombre o descripción del producto sugerido.")


@router.get(
    "/{customer_id}/suggested-sale",
    response_model=List[SuggestedProduct],
    summary="Obtener sugerencias de compra para un cliente",
    description="Devuelve productos sugeridos para un cliente según su historial de compras, popularidad y categorías frecuentes.",
    responses={
        200: {"description": "Sugerencia generada correctamente."},
        404: {"description": "El cliente no existe."},
    },
)
async def suggested_sale(
    customer_id: str = Path(
        ...,
        description="Código o identificador único del cliente para el cual se quiere sugerir una venta.",
        examples=["C001"],
    ),
    request: Request = None,
):
    sales_repo = request.app.state.sales_repo
    product_repo = request.app.state.product_repo
    settings = request.app.state.settings

    from app.services.recommendation_service import RecommendationService

    rec_svc = RecommendationService(product_repo, sales_repo, settings)
    try:
        items = rec_svc.suggest_for_customer(customer_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="customer not found")
    return items
