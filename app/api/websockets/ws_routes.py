import json
import traceback
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.core.websocket.event_dispatcher import EventDispatcher
from app.core.websocket.ws_manager import ws_manager
from app.db.db_chat import get_user_messages
# from app.services.websockets.ws_services import send_ws_message


import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["Web sockets flows && Webhooks"])

@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """
    Conexión WebSocket
    """
    try:
        # user_id = 1        
        # Si pasa la validación → conecta
        client_id = websocket.query_params.get("client_id")
        await ws_manager.connect(websocket,client_id)
        print(f"✅ Cliente WS conectado:")
        # Mantén la conexión abierta para recibir mensajes opcionales
        try:
            # Paso 2: Bucle que mantiene viva la conexión
            while True:
                data = await websocket.receive_text()
                print(f"📩 Mensaje recibido desde cliente: {data}")
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"error": "Formato JSON inválido."}))
                    continue
                
                # if isinstance(message, dict):
                #     message["client_id"] = client_id
                message_enriched = {
                    **message,      # Copia todo lo que envió el usuario
                    "client_id": client_id  # Añade tu info interna
                }
                # await ws_manager.handle_message(websocket, data)
                # 5. Delegar la lógica de negocio al Dispatcher, pasando el objeto websocket
                await EventDispatcher.dispatch(websocket, message_enriched)
                
        except WebSocketDisconnect as e:
            print(f"❌ Cliente desconectado por {e}")
            ws_manager.disconnect(websocket)
            # _ = await websocket.receive_text()

    except Exception as e:
        print(f"❌ Error o desconexión WS: {e}")
        await websocket.close(code=1008)


@router.get("/get-messages-user/{client_id}")
def get_chat_mesages(client_id: str):
    try:
        messages = get_user_messages(
                                    client_id
                                 )
        return messages
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"ERROR DETECTED AT :\n{error_trace}")
    