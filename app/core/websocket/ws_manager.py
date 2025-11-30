from typing import Any, List, Dict, Set
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
import json
import logging
# Importamos el Dispatcher, aunque lo usaremos en el endpoint, no aquí
logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Clase central para manejar las conexiones activas y difundir mensajes.
    """
    # user_id → list[WebSocket]
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Acepta la conexión y la añade, usando el user_id para agrupar conexiones."""
        await websocket.accept()
        setattr(websocket, 'user_id', user_id) # Adjuntamos el user_id
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WS conectado: usuario {user_id}. Total conexiones: {len(self.active_connections.get(user_id))}")

    def disconnect(self, websocket: WebSocket):
        """Remueve la conexión."""
        user_id = getattr(websocket, "user_id", None)
        if not user_id:
            return

        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass # Ya no estaba
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                logger.info(f"WS desconectado: usuario {user_id}. Última sesión cerrada.")

    async def _send_safe(self, ws: WebSocket, data: str):
        """Intenta enviar y gestiona la desconexión si falla."""
        try:
            await ws.send_text(data)
            return True
        except WebSocketDisconnect:
            self.disconnect(ws)
            return False
        except Exception as e:
            logger.error(f"Error enviando WS: {e}")
            self.disconnect(ws)
            return False

    async def broadcast(self, message: Dict[str, Any]):
        """Envía a TODOS los clientes activos (Broadcast Global)."""
        data = json.dumps(message)
        for user_id, connections in list(self.active_connections.items()):
            for ws in connections[:]:
                await self._send_safe(ws, data)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Envía a todas las conexiones de un usuario específico."""
        if user_id not in self.active_connections:
            logger.warning(f"Usuario {user_id} no está conectado.")
            return

        data = json.dumps(message)
        for ws in self.active_connections[user_id][:]:
            await self._send_safe(ws, data)

    async def send_to_channel_users(self, user_ids: Set[str], message: Dict[str, Any]):
        """
        MÉTODO CLAVE: Envía un mensaje a un conjunto de user_ids.
        Usado internamente por el EventDispatcher.
        """
        data = json.dumps(message)
        sent_count = 0
        
        for user_id in user_ids:
            if user_id in self.active_connections:
                for ws in self.active_connections[user_id][:]:
                    await self._send_safe(ws, data)
                    sent_count += 1
        
        logger.info(f"✉️ Evento de canal enviado a {len(user_ids)} usuarios suscritos. Total conexiones alcanzadas: {sent_count}.")
        
# Creamos una instancia única del manager que será importada en toda la aplicación
ws_manager = WebSocketManager()
