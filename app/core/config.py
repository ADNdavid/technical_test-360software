from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    GOOGLE_API_KEY: str | None = Field(None, env="GOOGLE_API_KEY")
    GOOGLE_EMBEDDING_MODEL: str = Field("gemini-embedding-001", env="GOOGLE_EMBEDDING_MODEL")
    PRODUCTS_EXCEL_PATH: Path = Field(Path("data/raw/productos.xlsx"), env="PRODUCTS_EXCEL_PATH")
    SALES_EXCEL_PATH: Path = Field(Path("data/raw/pedidos.xlsx"), env="SALES_EXCEL_PATH")
    TOP_K: int = Field(5, env="TOP_K")
    SUGGESTED_PRODUCTS_LIMIT: int = Field(5, env="SUGGESTED_PRODUCTS_LIMIT")
    EMBEDDINGS_CACHE_DIR: Path = Field(Path("data/embeddings"), env="EMBEDDINGS_CACHE_DIR")
    EMBEDDING_BATCH_SIZE: int = Field(16, env="EMBEDDING_BATCH_SIZE")

    class Config:
        env_file = ".env"
