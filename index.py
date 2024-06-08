from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import external

app = FastAPI(
    debug=True,
    docs_url="/api/docs",
    openapi_url="/api/v1/openapi.json",
)

app.include_router(external.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
