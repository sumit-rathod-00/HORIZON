# app/main.py

from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="HORIZON API",
    version="0.1.0"
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to HORIZON Backend 🚀"
    }