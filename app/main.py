from fastapi import FastAPI
from routers import materials
app = FastAPI()
app.include_router(materials.router)