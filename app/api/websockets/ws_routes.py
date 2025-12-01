import json
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket.event_dispatcher import EventDispatcher
from app.core.websocket.ws_manager import ws_manager
from app.db.db_chat import get_user_messages

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["Web sockets flows"])

@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """
        WebSocket connection endpoint.

        Handles incoming WebSocket connections from clients. The flow is:
        1. Retrieve client_id from query parameters.
        2. Register the WebSocket connection with the global ws_manager.
        3. Keep the connection open to continuously receive messages.
        4. Parse incoming messages as JSON. If invalid, return error message.
        5. Enrich the message object with client_id.
        6. Delegate the message to the EventDispatcher for business logic processing.
        7. Handle client disconnects gracefully.
        
        Args:
            websocket (WebSocket): The WebSocket connection object provided by FastAPI.

        Notes:
            - Uses the EventDispatcher singleton to manage all incoming WebSocket messages.
            - Delegates business logic to specific handlers based on message type.
            - Closes the WebSocket connection with code 1008 in case of unexpected errors.
    """
    try:     
        # 1
        client_id = websocket.query_params.get("client_id")
        # 2
        await ws_manager.connect(websocket,client_id)
        print(f"Client WS conected:")
        
        try:
            # 3
            while True:
                data = await websocket.receive_text()
                print(f"Received Message from the client: {data}")
                try:
                    # 4
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                    continue
                # 5
                message_enriched = {
                    **message,      # Copia todo lo que envió el usuario
                    "client_id": client_id  # Añadimos el clientId para que sea accesible posteriormente
                }
                # 6
                await EventDispatcher.dispatch(websocket, message_enriched)
        #7       
        except WebSocketDisconnect as e:
            print(f"Disconnected client by {e}")
            ws_manager.disconnect(websocket)
            
    except Exception as e:
        print(f"WS Error: {e}")
        await websocket.close(code=1008)


@router.get("/get-messages-user/{client_id}")
def get_chat_mesages(client_id: str):
    """
        Retrieve all chat messages for a given client.

        Args:
            client_id (str): The unique identifier for the client session.

        Returns:
            List[dict]: A list of chat messages with sender, content, and timestamp.

        Notes:
            - Delegates database access to `get_user_messages`.
            - Handles exceptions gracefully and logs traceback for debugging.
            - Suitable for frontend polling or initial chat history loading.
    """
    try:
        messages = get_user_messages(
                                    client_id
                                 )
        return messages
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error detected at :\n{error_trace}")
    