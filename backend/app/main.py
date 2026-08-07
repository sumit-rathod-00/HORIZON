# app/main.py

from fastapi import FastAPI

from app.api.v1.router import api_router

from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging

from app.middleware.logging import RequestLoggingMiddleware

from app.core.exceptions import ProjectNotFoundException


# --------------------------------------------------
# Logging
# --------------------------------------------------

setup_logging()


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="HORIZON API",
    version="0.1.0",
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)


# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

register_exception_handlers(app)


# --------------------------------------------------
# API Routers
# --------------------------------------------------

app.include_router(api_router)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Welcome to HORIZON Backend 🚀"
    }


# --------------------------------------------------
# Test Endpoint
# --------------------------------------------------

@app.get("/test")
async def test():
    raise ProjectNotFoundException()