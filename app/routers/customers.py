from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/{customer_id}/suggested-sale")
async def suggested_sale(customer_id: str, request: Request):
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
