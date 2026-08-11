# Ferretería - Búsqueda Semántica y Venta Sugerida

API de ejemplo que implementa búsqueda semántica de productos y recomendaciones basadas en historial de ventas.

Rápido inicio:

- Copiar `.env.example` a `.env` y completar `GOOGLE_API_KEY` si se dispone.
- Ejecutar:

```bash
pip install -r requirements.txt # o usar pyproject
uvicorn main:app --reload
```

Endpoints principales:
- `GET /health`
- `POST /products/search`
- `GET /customers/{customer_id}/suggested-sale`

Notas:
- Si `GOOGLE_API_KEY` no está definido, la aplicación genera embeddings determinísticos locales para desarrollo.
- Los datos de ejemplo están en `data/raw/`.
