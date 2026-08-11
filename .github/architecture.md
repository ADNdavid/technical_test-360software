# Prompt: Construcción de API de Búsqueda Semántica y Venta Sugerida para Ferretería

## Rol

Actúa como un arquitecto de software senior y desarrollador Python especializado en FastAPI, procesamiento de datos, embeddings, búsqueda semántica y sistemas de recomendación.

Tu objetivo es construir una API backend completa, modular, mantenible y ejecutable localmente para una ferretería, utilizando FastAPI, Python, Pandas, NumPy y Google GenAI Embeddings.

La aplicación debe cubrir dos funcionalidades principales:

1. Búsqueda semántica de productos de ferretería mediante embeddings de Google.
2. Generación de una venta sugerida basada en el historial de compras de un cliente.

Debes generar el código necesario, la estructura de carpetas, configuraciones, modelos, servicios, repositorios, endpoints, validaciones, manejo de errores, documentación y pruebas.

---

## 1. Contexto del negocio

La aplicación debe estar orientada a una ferretería que vende productos como:

- Tornillos, tuercas, arandelas y remaches
- Cables, conectores y accesorios eléctricos
- Tuberías, válvulas y accesorios de fontanería
- Herramientas manuales y eléctricas
- Adhesivos, selladores y cinta aislante
- Materiales de construcción diversos

El sistema debe permitir a un usuario describir un producto en lenguaje natural y encontrar productos similares, así como recomendar productos adicionales a clientes según su historial de compras.

---

## 2. Objetivo general

Construir una API REST con FastAPI capaz de:

### Proyecto 1 — Búsqueda semántica

Recibir una descripción libre escrita por un usuario, generar un embedding mediante el SDK oficial de Google y encontrar los 5 productos más similares almacenados en un archivo Excel.

Ejemplos de consulta:

- "Necesito un tornillo autorroscante de 1/2 pulgada"
- "Busco una llave ajustable para usar en mantenimiento eléctrico"
- "Quiero una cinta aislante de 20 metros"
- "Necesito una válvula de paso para agua"

La API debe devolver los cinco productos con mayor similitud semántica.

### Proyecto 2 — Venta sugerida

Recibir un customer_id, consultar el historial de compras almacenado en Excel y devolver una lista de productos que podrían ser ofrecidos al cliente en su próxima compra.

La respuesta debe ser estrictamente una lista de productos sugeridos, sin información innecesaria adicional.

---

## 3. Requisitos tecnológicos

Utiliza:

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic y Pydantic Settings
- Pandas
- NumPy
- Google GenAI SDK oficial (google-genai)
- scikit-learn opcionalmente para cálculo de similitud
- pytest
- httpx para pruebas de endpoints
- python-dotenv si es conveniente

No utilices frameworks innecesarios.
Prioriza una solución simple, modular y fácil de mantener.

---

## 4. Estructura del proyecto

Mantén una arquitectura clara y separada por responsabilidades. La estructura base puede ser:

```text
project/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── products.py
│   │   └── customers.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── semantic_search_service.py
│   │   └── recommendation_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── product_repository.py
│   │   └── sales_repository.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   └── utils/
│       ├── __init__.py
│       └── excel_loader.py
├── data/raw
│   ├── productos.xlsx
│   └── pedidos.xlsx
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── main.py
```

Debes mantener claramente separadas:

- Rutas HTTP
- Lógica de negocio
- Acceso a datos
- Integración con Google
- Configuración
- Pruebas

---

## 5. Configuración

La configuración debe manejarse con variables de entorno.

Crea un archivo .env.example con contenido similar a:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_EMBEDDING_MODEL=gemini-embedding-001
PRODUCTS_EXCEL_PATH=data/raw/productos.xlsx
SALES_EXCEL_PATH=data/raw/pedidos.xlsx
TOP_K=5
SUGGESTED_PRODUCTS_LIMIT=5
```

No hardcodees claves API ni valores sensibles.
Crea una clase de configuración con Pydantic Settings o una alternativa equivalente.

---

## 6. Carga de archivos Excel

La aplicación debe cargar los archivos Excel una sola vez en el startup/lifespan de FastAPI.

Implementa un componente responsable de:

1. Leer productos.xlsx
2. Leer pedidos.xlsx
3. Validar que los archivos existan
4. Validar que las columnas requeridas existan
5. Normalizar valores nulos
6. Normalizar tipos de datos cuando sea necesario
7. Mantener los DataFrames disponibles en memoria

Preferiblemente usa lifespan de FastAPI para cargar los datos una vez y almacenarlos en app.state.

No generes embeddings en cada request.

---

## 7. Estructura esperada del Excel de productos

Asume inicialmente que productos.xlsx contiene columnas como mínimo:

```text
PLU
descripcion
codpro
nompro
```

Si existen columnas adicionales, consérvalas si son útiles.
La definición de columnas debe centralizarse para que sea fácil adaptarla.

Para cada producto, crea un texto combinado para generar el embedding. Por ejemplo:

```text
Descripción: Tornillo autorroscante de 1/2 pulgada
Categoría: Ferretería general
Subcategoría: Tornillería
Marca: XYZ
```

El texto debe reflejar el dominio de ferretería y no usar ejemplos de tecnología.

---

## 8. Estructura esperada del Excel de pedidos

Asume que pedidos.xlsx o sales.xlsx puede contener columnas como mínimo:

```text
nitcli
codpro
descrip
cantped
vlrbruped
ivabruped
lrnetoped
estado
tipo
obsped
```

Si el archivo real usa otros nombres, deja la implementación preparada para mapearlos fácilmente mediante configuración o constantes.

---

## 9. Integración con Google Embeddings

Usa el SDK oficial google-genai.

Crea un servicio independiente en app/services/embedding_service.py que:

- Inicialice el cliente de Google
- Reciba texto y genere un embedding
- Permita generar embeddings para múltiples textos
- Maneje errores de API de forma segura
- No exponga credenciales ni información sensible

El modelo debe ser configurable con GOOGLE_EMBEDDING_MODEL.
No acoples el resto de la aplicación directamente al SDK de Google.

---

## 10. Indexación de productos

Durante el startup de la aplicación:

1. Carga los productos desde Excel
2. Construye el texto semántico de cada producto
3. Genera el embedding de cada producto
4. Guarda los embeddings en memoria
5. Mantiene una relación entre product_id, producto y embedding

La arquitectura debe permitir búsquedas eficientes y evitar recalcular embeddings en cada consulta.

---

## 11. Manejo de errores durante la indexación

Implementa manejo robusto de errores.

Si Google falla al generar embeddings:

- Registra el error con logging
- No expongas credenciales
- Devuelve un error claro si la aplicación no puede inicializarse correctamente
- Evita dejar la aplicación en un estado parcialmente inicializado

Considera también:

- DataFrame vacío
- Producto sin nombre o descripción
- Producto sin categoría
- Filas corruptas
- Archivo inexistente
- Error de conexión con Google

---

## 12. Endpoint de búsqueda semántica

Implementa:

```http
POST /products/search
```

Debe recibir un JSON como:

```json
{
  "query": "necesito una llave ajustable de 12 pulgadas"
}
```

Define un schema Pydantic:

```python
class ProductSearchRequest(BaseModel):
    query: str
```

Valida que:

- query no esté vacío
- se eliminen espacios innecesarios
- exista una longitud mínima razonable
- se rechacen valores inválidos

---

## 13. Procesamiento de la búsqueda

Cuando llegue una petición:

1. Recibir el texto de búsqueda
2. Generar el embedding de la consulta usando Google
3. Compararlo contra los embeddings de productos almacenados en memoria
4. Usar similitud de coseno
5. Ordenar de mayor a menor similitud
6. Seleccionar los primeros TOP_K productos

El valor TOP_K debe ser configurable mediante variables de entorno.

---

## 14. Respuesta esperada de búsqueda

La respuesta debe ser JSON con esta estructura:

```json
{
  "query": "necesito una llave ajustable de 12 pulgadas",
  "results": [
    {
      "product_id": "P001",
      "name": "Llave ajustable 12 pulgadas",
      "description": "Herramienta manual para uso general",
      "category": "Herramientas",
      "similarity": 0.9342
    }
  ]
}
```

La similitud debe devolverse como número decimal redondeado.
No agregues los embeddings en la respuesta.

---

## 15. Proyecto 2 — Venta sugerida

Implementa:

```http
GET /customers/{customer_id}/suggested-sale
```

La respuesta debe ser estrictamente una lista de productos sugeridos.

Ejemplo:

```json
[
  {
    "product_id": "P010",
    "product_name": "Tornillo autorroscante 1/2"
  },
  {
    "product_id": "P021",
    "product_name": "Cinta aislante 20 m"
  }
]
```

No agregues un wrapper como customer_id/recommendations.

---

## 16. Regla de recomendación

Implementa una estrategia híbrida sencilla y explicable:

### Prioridad 1
Productos que el cliente ha comprado anteriormente con mayor frecuencia.

### Prioridad 2
Productos de categorías que el cliente compra frecuentemente pero que aún no ha comprado.

### Prioridad 3
Si faltan candidatos, usar productos populares globalmente.

La lógica debe:

- Evitar duplicados
- Evitar productos inválidos
- Manejar clientes sin historial
- Manejar clientes inexistentes
- Ser determinística
- Ser fácilmente modificable

La lógica de negocio debe residir exclusivamente en app/services/recommendation_service.py.

---

## 17. Cantidad de recomendaciones

Define una configuración:

```env
SUGGESTED_PRODUCTS_LIMIT=5
```

Por defecto se recomendarán 5 productos, pero la implementación debe permitir cambiarlo fácilmente.

---

## 18. Clientes sin historial

Si el cliente existe pero no tiene compras:

- Usa productos más vendidos globalmente
- Si existe suficiente información, prioriza categorías relevantes del cliente

Si el cliente no existe, devuelve un error 404 con un mensaje claro.

---

## 19. Manejo de errores HTTP

Implementa respuestas HTTP adecuadas:

- 400 para request inválido
- 404 para cliente o recurso no encontrado
- 422 para validación de Pydantic
- 500 para error interno inesperado
- 503 para servicio externo no disponible

No expongas stack traces al usuario final. Registra los detalles técnicos con logging.

---

## 20. Swagger / OpenAPI

FastAPI debe exponer automáticamente:

- /docs
- /openapi.json

Los endpoints deben estar documentados con:

- Descripciones
- Tags
- Schemas de request y response
- Ejemplos
- Códigos HTTP esperados

Los tags mínimos deben ser:

- Products
- Customers

---

## 21. Health Check

Agrega:

```http
GET /health
```

Respuesta:

```json
{
  "status": "ok"
}
```

Este endpoint no debe depender de búsquedas ni de procesos pesados.

---

## 22. Logging

Configura logging adecuadamente para registrar:

- Inicio de la aplicación
- Carga de Excel
- Cantidad de productos cargados
- Cantidad de ventas cargadas
- Inicio y finalización de indexación
- Errores de Google
- Errores de procesamiento

Nunca registres API keys ni credenciales.

---

## 23. Testing

Crea pruebas con pytest que cubran, como mínimo:

### Búsqueda semántica
- Query válida
- Query vacía
- Retorno de máximo 5 productos
- Orden descendente por similitud
- DataFrame sin productos
- Error del servicio de embeddings

### Venta sugerida
- Cliente existente con historial
- Cliente inexistente
- Cliente sin historial
- Eliminación de duplicados
- Priorización por frecuencia
- Límite máximo de recomendaciones

### API
- GET /health
- POST /products/search
- GET /customers/{customer_id}/suggested-sale

No dependas de llamadas reales a Google en las pruebas; usa mocks para el servicio de embeddings.

---

## 24. Separación de responsabilidades

Respeta estas responsabilidades estrictamente:

- Router: recibir request, validar datos, invocar servicios y devolver respuestas
- Service: reglas de negocio, cálculo de similitud, recomendaciones y procesamiento semántico
- Repository: acceso a DataFrames y consultas en memoria
- Embedding Service: comunicación con Google y generación de embeddings
- Configuration: variables de entorno, paths, modelos y límites

---

## 25. Rendimiento

Optimiza la aplicación considerando que:

- Los Excel se cargan una sola vez
- Los embeddings de productos se calculan una sola vez durante la indexación
- Las búsquedas usan vectores ya calculados en memoria
- Las consultas al historial usan índices en memoria
- No se debe leer el Excel desde disco en cada request

Usa operaciones vectorizadas de NumPy o scikit-learn siempre que sea posible.

---

## 26. Compatibilidad con cambios futuros

La arquitectura debe permitir en el futuro:

- Cambiar Google por otro proveedor de embeddings
- Migrar a una base de datos
- Usar un vector database
- Añadir filtros por categoría o precio
- Ajustar el algoritmo de recomendación
- Añadir autenticación y nuevos endpoints

No implementes esas funcionalidades todavía, pero evita una arquitectura que las haga difíciles.

---

## 27. Dependencias

Genera un pyproject.toml con dependencias como mínimo:

```text
fastapi
uvicorn
pandas
numpy
scikit-learn
google-genai
pydantic
pydantic-settings
python-dotenv
openpyxl
pytest
httpx
```

---

## 28. Datos de ejemplo

Si no hay archivos Excel reales, crea datos de ejemplo claramente identificados en data/raw.

Los datos deben permitir probar:

- Búsqueda semántica por palabras del dominio ferretería
- Clientes con historial de compras
- Clientes sin historial
- Diferentes categorías
- Productos repetidos en compras

No mezcles datos de ejemplo con código de producción.

---

## 29. Criterios de aceptación

La implementación será considerada correcta si cumple todos estos criterios:

- FastAPI inicia correctamente
- Los Excel se cargan una sola vez en el startup
- Los productos se indexan mediante embeddings
- Se utiliza el SDK oficial de Google
- La API key se obtiene desde variables de entorno
- POST /products/search funciona correctamente
- La búsqueda usa similitud de coseno
- La búsqueda devuelve máximo 5 productos
- Los resultados están ordenados por similitud descendente
- Los embeddings no aparecen en las respuestas
- GET /customers/{customer_id}/suggested-sale funciona
- Las recomendaciones usan el historial de compras
- No se generan productos duplicados
- Se maneja correctamente un cliente inexistente
- Se maneja correctamente un cliente sin historial
- La respuesta de venta sugerida es estrictamente una lista
- Existe GET /health
- Swagger funciona en /docs
- OpenAPI funciona en /openapi.json
- Existen pruebas automatizadas
- Las pruebas no requieren llamadas reales a Google
- Existe .env.example
- Existe README.md
- El código está separado por responsabilidades
- No existen credenciales hardcodeadas

---

## 30. Instrucción final para el desarrollador

Construye la aplicación completa y funcional, no solo una propuesta de arquitectura.
Asegúrate de que el resultado final sea ejecutable, mantenible y alineado con el contexto de una ferretería, usando ejemplos y nomenclaturas propias del negocio.

