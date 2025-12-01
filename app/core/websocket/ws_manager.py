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

    async def connect(self, websocket: WebSocket, client_id: str):
        """Acepta la conexión y la añade, usando el user_id para agrupar conexiones."""
        #Aceptamos la conexión
        await websocket.accept()
        
        # Guardamos el id en el objeto websocket para referencia futura
        websocket.client_id = client_id
        # setattr(websocket, 'user_id', user_id, 'client_id',client_id) # Adjuntamos el user_id
        
        if client_id not in self.active_connections:
            # self.active_connections[user_id] = []
            self.active_connections[client_id] = []

        # self.active_connections[user_id].append(websocket)
        self.active_connections[client_id].append(websocket)
        # logger.info(f"WS conectado: usuario {user_id}. Total conexiones: {len(self.active_connections.get(user_id))}")
        logger.info(f"WS conectado: cliente {client_id}. Total conexiones: {len(self.active_connections.get(client_id))}")
        

    def disconnect(self, websocket: WebSocket):
        """Remueve la conexión."""
        # Recuperamos el client_id que guardamos al conectar
        client_id = getattr(websocket, "client_id", None)
        
        if client_id and client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                try:
                    self.active_connections[client_id].remove(websocket)
                except ValueError:
                    pass # Ya no estaba
            
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                logger.info(f"Cliente {client_id} desconectado totalmente.")

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
        
    async def send_to_user(self, client_id: str, message: Dict[str, Any]):
        """Envía a todas las conexiones de un usuario específico."""
        if client_id not in self.active_connections:
            logger.warning(f"Cliente {client_id} no está conectado.")
            return
        
        data = json.dumps(message)
        sent_count = 0
        for ws in self.active_connections[client_id][:]:
            if await self._send_safe(ws, data):
                sent_count += 1
        
        logger.info(f"✉️ Respuesta enviada al cliente {client_id}. Conexiones alcanzadas: {sent_count}.")
                 
# Creamos una instancia única del manager que será importada en toda la aplicación
ws_manager = WebSocketManager()
