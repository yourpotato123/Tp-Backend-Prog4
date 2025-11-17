from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routes.autos import router as autos_router
from routes.ventas import router as ventas_router

app = FastAPI(title="API Ventas de Autos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(autos_router)
app.include_router(ventas_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "API Ventas de Autos - FastAPI + SQLModel"}
