from typing import List
import numpy as np

class RecommendationService:
    def __init__(self, product_repo, sales_repo, settings):
        self.product_repo = product_repo
        self.sales_repo = sales_repo
        self.settings = settings

    def suggest_for_customer(self, customer_id: str) -> List[dict]:
        # check existence
        if not self.sales_repo.customer_exists(customer_id):
            raise KeyError("Customer not found")

        purchases = self.sales_repo.purchases_by_customer(customer_id)
        if purchases.empty:
            # fallback to popular products
            popular = self.sales_repo.most_popular_products(self.settings.SUGGESTED_PRODUCTS_LIMIT)
            return self._products_by_ids(popular)

        # priority 1: products bought previously by frequency
        freq = purchases.groupby('codpro')['cantped'].sum().reset_index().sort_values('cantped', ascending=False)
        bought_ids = list(freq['codpro'].astype(str).values)

        results = []
        seen = set()
        for pid in bought_ids:
            if pid in seen:
                continue
            seen.add(pid)
            results.append(pid)
            if len(results) >= self.settings.SUGGESTED_PRODUCTS_LIMIT:
                return self._products_by_ids(results)

        # priority 2: categories frequently bought but not purchased
        merged = purchases.merge(self.product_repo.products, left_on='codpro', right_on='codpro', how='left')
        top_cats = merged['categoria'].value_counts().index.tolist()
        for cat in top_cats:
            candidates = self.product_repo.products[self.product_repo.products.get('categoria','')==cat]
            for _, row in candidates.iterrows():
                pid = str(row.get('codpro'))
                if pid in seen:
                    continue
                seen.add(pid)
                results.append(pid)
                if len(results) >= self.settings.SUGGESTED_PRODUCTS_LIMIT:
                    return self._products_by_ids(results)

        # priority 3: global popular
        popular = self.sales_repo.most_popular_products(50)
        for pid in popular:
            if pid in seen:
                continue
            seen.add(pid)
            results.append(pid)
            if len(results) >= self.settings.SUGGESTED_PRODUCTS_LIMIT:
                break

        return self._products_by_ids(results)

    def _products_by_ids(self, ids: List[str]) -> List[dict]:
        out = []
        for pid in ids[: self.settings.SUGGESTED_PRODUCTS_LIMIT]:
            df = self.product_repo.products
            row = df[df['codpro'].astype(str) == str(pid)]
            if row.empty:
                continue
            row = row.iloc[0]
            out.append({"product_id": str(row.get('codpro')), "product_name": row.get('nompro')})
        return out
