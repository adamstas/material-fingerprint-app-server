from fastapi import FastAPI

from app.models.material import Base
from app.routers import materials
from app.db.database import engine
app = FastAPI()

Base.metadata.create_all(bind=engine)  # creates all tables based on models
app.include_router(materials.router)

__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)