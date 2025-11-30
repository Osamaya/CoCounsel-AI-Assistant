from typing import Callable, Awaitable, Dict, Any, Optional
import logging

from fastapi import WebSocket

# Importamos el Manager para que el Dispatcher pueda emitir mensajes de salida (broadcast)
from app.core.websocket.ws_manager import ws_manager
from app.core.websocket.suscription_manager import subscription_manager 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define el tipo de handler para mensajes entrantes de clientes
Handler = Callable[[WebSocket, Dict[str, Any]], Awaitable[None]]

class EventDispatcher:
    """
    Despachador central de eventos (Mediator): 
    Mapea el canal (e.g., 'notify') a una función de negocio (handler).
    """
    # _handlers: Dict[str, Callable] = {}
    _handlers: Dict[str, Handler] = {}
    
    @classmethod
    def register(cls, channel: str, handler: Handler):
        cls._handlers[channel] = handler

    @classmethod
    async def dispatch(cls, websocket: WebSocket, message: Dict[str, Any]):
        """Recibe un mensaje de entrada de un cliente y lo dirige al handler."""
        channel = message.get("channel")
        handler = cls._handlers.get(channel)
        if handler:
            await handler(websocket, message)
        else:
            logger.warning(f"⚠️ No hay handler para canal '{channel}' (mensaje de cliente).")

    @classmethod
    async def emit(cls, message: Dict[str, Any], target_user_id: Optional[str] = None):
        """
        Método de ALTO NIVEL para que los servicios envíen mensajes.
        Decide si es dirigido (target_user_id) o por canal (Pub/Sub).
        """
        channel = message.get("channel")
        
        if target_user_id:
            # Opción 1: Mensaje dirigido a un único usuario (ej. notificaciones privadas)
            await ws_manager.send_to_user(target_user_id, message)
        
        elif channel:
            # Opción 2: Mensaje dirigido por canal (Pub/Sub: solo a suscritos)
            user_ids = subscription_manager.get_users_for_channel(channel)
            if user_ids:
                await ws_manager.send_to_channel_users(user_ids, message)
            else:
                logger.warning(f"Emit fallido: Canal '{channel}' existe, pero nadie está suscrito.")

        else:
            # Opción 3: Broadcast Global (Solo para eventos muy públicos, casi nunca recomendado)
            await ws_manager.broadcast(message)
