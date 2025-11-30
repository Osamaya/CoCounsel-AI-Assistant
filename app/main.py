from datetime import datetime
from functools import lru_cache,partial
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
from fastapi import Depends, File, Form, HTTPException, FastAPI, APIRouter,BackgroundTasks, Request, UploadFile
from pathlib import Path
from pydantic import BaseModel

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)


# Importa la función que necesites
logger = logging.getLogger(__name__)

app = FastAPI()

# --- SERVIR STATIC ---
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
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