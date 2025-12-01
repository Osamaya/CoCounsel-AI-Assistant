from fastapi.responses import  FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from fastapi import FastAPI
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio

# Import the AI Agent task (Consumer)
from app.services.ai_agent import run_ai_agent

"""
    FastAPI Lifespan: Used to manage background services.
    It ensures the AI Agent (Consumer) starts when the app launches.
    References: https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
@asynccontextmanager
async def lifespan(app: FastAPI):
   # Start the AI Agent in the background as an asynchronous task
    ai_tasks = asyncio.create_task(run_ai_agent())
    print("Starting AI Agent Service...")
    yield # Application is now ready to receive requests
    
    # Clean up on shutdown
    ai_tasks.cancel()
    print("Service stopped.")


logger = logging.getLogger(__name__)

# Initialize FastAPI with the lifespan context manager
app = FastAPI(lifespan=lifespan)

# --- SERVING STATIC FILES---
BASE_DIR = Path(__file__).resolve().parent

# Mount the static directory for serving CSS, JS, etc (Our frontend).
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Serve index.html as the homepage
@app.get("/")
def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")


""" INCLUDE WEBSOCKET ROUTER """
from app.api.websockets.ws_routes import router as ws_router
app.include_router(ws_router)

""" INITIALIZE WS EVENT DISPATCHER HANDLERS """
# Registers the 'chat' channel to its specific handler (e.g., chat_handler.py)
from app.core.websocket.init_dispatchers import initialize_ws_handlers as ws_init_routers
ws_init_routers()