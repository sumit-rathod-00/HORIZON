from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import HorizonException
from app.schemas.response import ApiResponse


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HorizonException)
    async def horizon_exception_handler(
        request: Request,
        exc: HorizonException,
    ):
        response = ApiResponse(
            success=False,
            message=exc.message,
            data=None,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ):
        response = ApiResponse(
            success=False,
            message="Internal Server Error",
            data=None,
        )

        return JSONResponse(
            status_code=500,
            content=response.model_dump(),
        )