from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import init_db
from backend.routes.dbs import router as dbs_router
from backend.routes.query import router as query_router
from backend.routes.nl_query import router as nl_query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="DB Query Tool", version="0.1.0", lifespan=lifespan)

# CORS — allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Unified global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "INTERNAL_ERROR",
                "message": f"服务器内部错误: {exc}",
                "location": "server",
            }
        },
    )

# Register routers
app.include_router(dbs_router, prefix="/api/v1")
app.include_router(query_router, prefix="/api/v1")
app.include_router(nl_query_router, prefix="/api/v1")
