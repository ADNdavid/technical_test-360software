# Ferretería — Búsqueda Semántica

 **Resumen del proyecto:**
 - Objetivo: API que permite búsqueda semántica de productos y sugerencias de venta basadas en historial de compras.
 - La aplicación procesa datos de inventario y utiliza embeddings para comparar consultas de usuario con productos.

 **Tecnologías principales:**
    <p align="left">
        <a href="https://skillicons.dev" target="blank">
            <img src="https://skillicons.dev/icons?i=py,fastapi,docker,git,sklearn&theme=light&perline=8" />
        </a>
    </p>

 - `FastAPI`: framework para construir la API REST.
 - `Docker` + `docker-compose`: contenedores reproducibles para despliegue/desarrollo.
 - `Pandas` / `OpenPyXL`: carga y limpieza de datos desde Excel/CSV.
 - `Scikit-learn`: cálculo de similitud coseno para la búsqueda de productos.

 Requisitos
 - Python >= 3.13
 - Docker (opcional para levantar contenedores)
 - Opcional: `GOOGLE_API_KEY` para embeddings reales vía Google Gemini

## Instalación y Uso

Clonar el repositorio:
```bash
git clone https://github.com/ADNdavid/technical_test-360software
cd technical_test-360software
```

  Instalación (local, sin Docker)
 1. Instalar el gestor de paquetes `UV`:

 ```bash
 python -m pip install --upgrade uv
 ```

 2. Crear y activar el entorno virtual:

 ```bash
 uv venv
 source .venv/Scripts/activate
 ```

 3. Instalar dependencias desde `pyproject.toml` hacia el entorno virtual:

 ```bash
 uv sync
 ```

 Ejecución
 - Con Docker (recomendado para reproducibilidad):

 ```bash
 docker compose up --build
 ```

 - Sin Docker:

 ```bash
 uvicorn main:app --reload
 ```

## Endpoints principales
 - `GET /health`
 - `POST /products/search`
 - `GET /customers/{customer_id}/suggested-sale`

## Comportamiento de embeddings
 - Si `GOOGLE_API_KEY` está configurada y disponible, se usan embeddings de Google.
 - Si no, la aplicación puede caer a embeddings locales determinísticos para desarrollo y pruebas.
 - La indexación de productos se realiza en background al iniciar la app y utiliza caché en `data/embeddings/`.

## Datos
 - Los archivos de productos y ventas deben estar en `data/raw/`.
 - El cargador soporta `.xlsx`, `.xls` y `.csv`.
 - Los datos se limpian automáticamente al cargar (trim de espacios y normalización).

## Author

<h3 style="font-family: 'Agency FB', sans-serif;">Anderson David Sepúlveda</h3>
<p align="left">
  <a href="https://linkedin.com/in/adndavid" target="blank">
    <img src="https://skillicons.dev/icons?i=linkedin&theme=light" />
  </a>
  <a href="https://github.com/ADNdavid" target="blank">
    <img src="https://skillicons.dev/icons?i=github&theme=light" />
  </a>
</p>
