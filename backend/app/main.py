# app/main.py

from fastapi import FastAPI

from app.api.v1.router import api_router

from app.core.handlers import register_exception_handlers

app = FastAPI(
    title="HORIZON API",
    version="0.1.0"
)

register_exception_handlers(app)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to HORIZON Backend 🚀"
    }

from app.core.exceptions import ProjectNotFoundException

@app.get("/test")
async def test():
    raise ProjectNotFoundException()