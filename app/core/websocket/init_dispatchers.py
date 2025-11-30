from app.core.websocket.event_dispatcher import EventDispatcher
from app.api.websockets.handlers.chat_handler import handle_chats_event
import logging

logger = logging.getLogger(__name__)

def initialize_ws_handlers():
    logger.info("🧩 Registrando handlers WS...")

    EventDispatcher.register("chat", handle_chats_event)
    logger.info("✅ Handlers WS inicializados correctamente")
