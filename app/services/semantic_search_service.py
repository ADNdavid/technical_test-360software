import numpy as np
from app.repositories.product_repository import ProductRepository


class SemanticSearchService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        return self.product_repo.top_k_similar(query_embedding, k=top_k)
