from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from config.database import mongodb_client
from routers.flow import router as flow_router
from routers.submission import router as submission_router
from routers.agent import router as agent_router
from routers.settings import router as settings_router
import logging

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    try:
        await mongodb_client.client.admin.command("ping")
        logger.info("MongoDB conectado")
    except Exception as e:
        logger.error(f"Erro ao conectar MongoDB: {e}")

    yield

    await mongodb_client.close()
    logger.info("Aplicacao encerrada")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend FlowQuote - Construtor visual de orcamentos",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    try:
        await mongodb_client.client.admin.command("ping")
        return {"status": "healthy", "mongodb": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "mongodb": str(e)}


app.include_router(flow_router)
app.include_router(submission_router)
app.include_router(agent_router)
app.include_router(settings_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.debug)
