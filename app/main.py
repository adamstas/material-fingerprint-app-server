from fastapi import FastAPI

from app.models.material import Base
from app.routers import materials
from app.db.database import engine
app = FastAPI(
    title="MatTag Server",
    description="API for material fingerprinting and analysis",
    version="0.7.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

Base.metadata.create_all(bind=engine)  # creates all tables based on models
app.include_router(materials.router)

__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)