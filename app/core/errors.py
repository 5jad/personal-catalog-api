from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    # Unified HTTPException response
    content = {
        "error": {
            "type": "http",
            "status_code": exc.status_code,
            "message": exc.detail,
        }
    }
    return JSONResponse(status_code=exc.status_code, content=content)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Provide a concise validation error payload
    errors = exc.errors()
    logger.debug("Validation error: %s", errors)
    return JSONResponse(status_code=422, content={"error": {"type": "validation", "details": errors}})

async def unexpected_exception_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error: %s", exc)
    return JSONResponse(status_code=500, content={"error": {"type": "internal", "message": "Internal server error"}})
