from typing import Callable, Awaitable, Dict, Any, Optional
import logging

from fastapi import WebSocket

# Import Manager for sending messages (output functionality)
from app.core.websocket.ws_manager import ws_manager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the expected signature for an incoming message handler
Handler = Callable[[WebSocket, Dict[str, Any]], Awaitable[None]]

class EventDispatcher:
    """
        Pattern: Mediator / Event Dispatcher. 
        Purpose: Central routing for both INBOUND (from client) and OUTBOUND (from services) messages.
    """
    # _handlers: Dict[str, Callable] = {}
    _handlers: Dict[str, Handler] = {}
    
    @classmethod
    def register(cls, channel: str, handler: Handler):
        """Register a handler function to a specific channel (e.g., 'chat' -> handle_chats_event)."""
        cls._handlers[channel] = handler

    @classmethod
    async def dispatch(cls, websocket: WebSocket, message: Dict[str, Any]):
        """Route an INBOUND message from a client to the registered business handler."""
        channel = message.get("channel")
        handler = cls._handlers.get(channel)
        if handler:
            await handler(websocket, message)
        else:
            logger.warning(f"No handler registered for channel '{channel}' (client message).")

    @classmethod
    async def emit(cls, message: Dict[str, Any], target_client: Optional[str] = None):
        """
            Route an OUTBOUND message from a service (e.g., AI Agent) to the target client.
            The AI Agent uses this method to send its response back.
        """
        channel = message.get("channel")
        
        if target_client:
            # Option 1: Directed message (Used by AI Agent for its response)
            await ws_manager.send_to_user(target_client, message)
        
        elif channel:
            print(f"Connected by the channel {channel}")
            # Option 2: Channel Pub/Sub (Broadcast to all subscribers of a channel) I delete this solution because we wouldn't need it
            # user_ids = subscription_manager.get_users_for_channel(channel)
            # if user_ids:
                # await ws_manager.send_to_channel_users(user_ids, message)
            # else:
                # logger.warning(f"Emit fallido: Canal '{channel}' existe, pero nadie está suscrito.")
