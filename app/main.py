from fastapi import FastAPI

from .api.routes import router as url_router
from .database import Base, engine


# Criação das tabelas (camada de modelo / persistência)
Base.metadata.create_all(bind=engine)


# "Application factory" simples
app = FastAPI(title="URL Shortener")

# Registro das rotas da camada de API (Controllers)
app.include_router(url_router)

