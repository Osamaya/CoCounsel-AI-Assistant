from app.core.websocket.event_dispatcher import EventDispatcher
from app.api.websockets.handlers.chat_handler import handle_chats_event
import logging

logger = logging.getLogger(__name__)

"""
    Initializes all WebSocket event handlers for the application.
    
    This function is responsible for registering the appropriate 
    handlers for different WebSocket channels. Currently, it 
    registers the 'chat' channel handler to process incoming chat events (can be any channel).
    
    Usage:
        Call this function once at application startup to ensure all
        WebSocket channels are properly wired to their handlers.
"""
def initialize_ws_handlers():
    logger.info("Registering WebSocket handlers...")
    EventDispatcher.register("chat", handle_chats_event)
    logger.info("WebSocket handlers initialized successfully")
