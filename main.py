from fastapi import FastAPI
from routers import films, users

app = FastAPI()

# Url local: http://127.0.0.1:8000
# Documentación con Swagger: http://127.0.0.1:8000/docs
# Documentación con Redocly: http://127.0.0.1:8000/redoc

app.include_router(films.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return "Hola FastAPI!"