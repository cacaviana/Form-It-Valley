from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config.settings import settings
from config.database import mongodb_client
from routers.flow import router as flow_router
from routers.agent import router as agent_router
from routers.settings import router as settings_router
from routers.activecampaign import router as activecampaign_router
from routers.notifications import router as notifications_router
from routers.scheduling import router as scheduling_router
from routers.auth import router as auth_router
from routers.public import router as public_router
from routers.users import router as users_router
from routers.scheduling_config import router as scheduling_config_router
from routers.whatsapp import router as whatsapp_router
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# Rotas publicas (sem auth)
app.include_router(auth_router)
app.include_router(public_router)

# Rotas protegidas (requerem JWT)
from itvalleysecurity.fastapi import require_access
from fastapi import Depends

protected = {"dependencies": [Depends(require_access)]}
app.include_router(flow_router, **protected)
app.include_router(agent_router, **protected)
app.include_router(settings_router, **protected)
app.include_router(activecampaign_router, **protected)
app.include_router(notifications_router, **protected)
app.include_router(scheduling_router, **protected)
app.include_router(users_router, **protected)
app.include_router(scheduling_config_router, **protected)
app.include_router(whatsapp_router, **protected)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.debug)
