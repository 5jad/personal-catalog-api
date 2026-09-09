from fastapi import FastAPI
from app.routers import auth, warehouses, products, exports

app = FastAPI(title="Personal Catalog API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(products.router, prefix="/warehouses/{warehouse_id}/products", tags=["products"])
app.include_router(exports.router, prefix="/warehouses/{warehouse_id}/exports", tags=["exports"])

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
