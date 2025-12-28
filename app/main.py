from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="Secure RAG PoC", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Secure RAG System is Online"}
