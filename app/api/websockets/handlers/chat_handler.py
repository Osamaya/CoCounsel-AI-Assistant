# app/api/websockets/handlers/chat_handler.py
from fastapi import WebSocket
from app.core.websocket.event_bus import event_bus
from app.db.db_chat import *

async def handle_chats_event(websocket: WebSocket, message: dict):
    """
    Recibe un mensaje de chat y lo publica en el Event Bus para procesamiento asíncrono.
    """
    tipo = message.get("type")
    payload = message.get("payload", {})
    client_id = message.get("client_id")

    if tipo == "NEW_USER_MESSAGE":
        user_text = payload.get("text")
        
        # 1. TODO: Persistencia (Guardar el mensaje de entrada en SQLite)
        session_id = get_sessions_or_create(client_id)
        save_message(session_id, "user",  user_text)
        
        # 2. Publicar al Event Bus (Caja de comandas para el Chef)
        event_payload = {
            "type": "PROCESS_AI_REQUEST", 
            "client_id": client_id,
            "text": user_text,
            "timestamp": payload.get("timestamp")
        }
        
        await event_bus.publish_to_ia(event_payload)
        # La función termina aquí inmediatamente.
        
    else:
        print(f"⚠️ Tipo de evento '{tipo}' no manejado por el handler CHAT.")