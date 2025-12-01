from fastapi.responses import  FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from fastapi import FastAPI
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio

#Importamos el agente
from app.services.ai_agent import run_ai_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Arrancamos el agente el el background
    ai_tasks = asyncio.create_task(run_ai_agent())
    print("Iniciando el servicio AGENTE")
    yield
    
    ai_tasks.cancel()
    print("Servicio detenido")

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

# --- SERVIR STATIC ---
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Servir index.html como homepage
@app.get("/")
def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")


"""INCLUIMOS LA LÓGICA Y APERTURA DE LOS WEBSOCKETS"""
from app.api.websockets.ws_routes import router as ws_router
app.include_router(ws_router)

"""INICIALIZAMOS EL DISPATCHER DEL ROUTER """
from app.core.websocket.init_dispatchers import initialize_ws_handlers as ws_init_routers
ws_init_routers()