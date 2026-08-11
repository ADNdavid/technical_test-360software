from pathlib import Path
from typing import Iterable
from app.core.config import Settings
from app.utils.excel_loader import load_table, REQUIRED_SALES_COLUMNS

class SalesRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sales = load_table(Path(settings.SALES_EXCEL_PATH), required_columns=None)

    def customer_exists(self, customer_id: str) -> bool:
        return customer_id in self.sales.get('nitcli', []).astype(str).values

    def purchases_by_customer(self, customer_id: str):
        df = self.sales[self.sales['nitcli'].astype(str) == str(customer_id)]
        return df

    def most_popular_products(self, limit: int = 10):
        grp = self.sales.groupby('codpro')['cantped'].sum().reset_index()
        grp = grp.sort_values('cantped', ascending=False)
        return list(grp['codpro'].astype(str).head(limit).values)

    def categories_for_customer(self, customer_id: str, products_df):
        df = self.purchases_by_customer(customer_id)
        merged = df.merge(products_df, left_on='codpro', right_on='codpro', how='left')
        return merged.get('categoria', '').fillna('')
