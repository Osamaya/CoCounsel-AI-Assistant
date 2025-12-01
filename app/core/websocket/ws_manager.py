from typing import Any, List, Dict, Set
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
import json
import logging
logger = logging.getLogger(__name__)

class WebSocketManager:
    """
        Pattern: Singleton (via global instantiation) & Connection Abstraction.
        Purpose: Central class for managing active connections, mapping the client_id 
        (session ID) to the WebSocket object(s).
    """
    
    # user_id -> list[WebSocket]
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accepts the connection and maps it using the client_id (session ID)."""
        await websocket.accept()
        
        # Store ID on the object for easy retrieval
        websocket.client_id = client_id
        # setattr(websocket, 'user_id', user_id, 'client_id',client_id) # Adjuntamos el user_id
        
        if client_id not in self.active_connections:
            # self.active_connections[user_id] = []
            self.active_connections[client_id] = []

        # self.active_connections[user_id].append(websocket)
        self.active_connections[client_id].append(websocket)
        # logger.info(f"WS conectado: usuario {user_id}. Total conexiones: {len(self.active_connections.get(user_id))}")
        logger.info(f"WS connected: client {client_id}. Total connections: {len(self.active_connections.get(client_id))}")
        

    def disconnect(self, websocket: WebSocket):
        """Removes the connection upon close or error."""
        # Retrieve the client_id from the WS object
        client_id = getattr(websocket, "client_id", None)
        
        if client_id and client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                try:
                    self.active_connections[client_id].remove(websocket)
                except ValueError:
                    pass
            
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                logger.info(f"Client {client_id} completely logout")

    async def _send_safe(self, ws: WebSocket, data: str):
        """Intenta enviar y gestiona la desconexión si falla."""
        try:
            await ws.send_text(data)
            return True
        except WebSocketDisconnect:
            self.disconnect(ws)
            return False
        except Exception as e:
            logger.error(f"Error sending WS: {e}")
            self.disconnect(ws)
            return False
        
    async def send_to_user(self, client_id: str, message: Dict[str, Any]):
        """
            Core outbound method. Sends a message to ALL connections associated 
            with a single client_id (e.g., if the user has multiple tabs open).
            Used by the EventDispatcher when the AI Agent responds.
        """
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} id not conected.")
            return
        
        data = json.dumps(message)
        sent_count = 0
        for ws in self.active_connections[client_id][:]:
            if await self._send_safe(ws, data):
                sent_count += 1
        
        logger.info(f"Response sent to client {client_id}. Connections reached: {sent_count}.")
                 
# Create a single instance (Singleton Pattern)
ws_manager = WebSocketManager()
