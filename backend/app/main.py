import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError
from .database.mongodb import database_status, ensure_indexes, ping_database
from .routers import assistant, auth, dashboard, products, transactions

app = FastAPI(title="VyaparVoice API", version="2.0.0")
origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5175").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$", allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(assistant.router)

@app.on_event("startup")
def startup():
    try:
        ensure_indexes()
    except PyMongoError:
        pass

@app.get("/api/health")
def health():
    try:
        ping_database()
        return {"status": "ok", "database": "connected"}
    except PyMongoError:
        raise HTTPException(status_code=503, detail={"status": "error", "database": "disconnected"})
