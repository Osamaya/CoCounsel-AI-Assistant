from fastapi import WebSocket
from app.core.websocket.event_bus import event_bus
from app.db.db_chat import *

async def handle_chats_event(websocket: WebSocket, message: dict):
    """
        Handle incoming chat events from clients.

        Args:
            websocket (WebSocket): The client WebSocket connection.
            message (dict): The message payload containing type, payload, client_id.

        Flow:
            1. Extract type, payload, and client_id.
            2. If type is "NEW_USER_MESSAGE":
                a. Persist the message to the database.
                b. Enrich and publish to Event Bus for AI processing.
            3. Ignore unsupported message types with a warning log.
        
        Notes:
            - This function is designed to be async to allow non-blocking operations.
            - Persists user messages and triggers AI response asynchronously.
            - Acts as a handler for the "chat" channel in EventDispatcher.
    """
    tipo = message.get("type")
    payload = message.get("payload", {})
    client_id = message.get("client_id")

    if tipo == "NEW_USER_MESSAGE":
        user_text = payload.get("text")
        
        # TODO: Persistencia (Guardamos el mensaje de entrada en SQLite)
        session_id = get_sessions_or_create(client_id)
        save_message(session_id, "user",  user_text)
        
        #Publicamos al Event Bus
        event_payload = {
            "type": "PROCESS_AI_REQUEST", 
            "client_id": client_id,
            "text": user_text,
            "timestamp": payload.get("timestamp")
        }
        
        await event_bus.publish_to_ia(event_payload)
       
        
    else:
        print(f"Event type '{tipo}' unmanaged by the handler CHAT.")