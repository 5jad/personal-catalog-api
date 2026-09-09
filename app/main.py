from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from app.routers import auth, warehouses, products, exports
from app.core import errors as error_handlers

app = FastAPI(title="Personal Catalog API")

# Register unified exception handlers
app.add_exception_handler(HTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, error_handlers.validation_exception_handler)
app.add_exception_handler(Exception, error_handlers.unexpected_exception_handler)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(products.router, prefix="/warehouses/{warehouse_id}/products", tags=["products"])
app.include_router(exports.router, prefix="/warehouses/{warehouse_id}/exports", tags=["exports"])

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
