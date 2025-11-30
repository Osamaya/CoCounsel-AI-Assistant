import json
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.core.websocket.event_dispatcher import EventDispatcher
from app.core.websocket.ws_manager import ws_manager
# from app.services.websockets.ws_services import send_ws_message


router = APIRouter(prefix="/ws", tags=["Web sockets flows && Webhooks"])

@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """
    Conexión WebSocket autenticada mediante cookie JWT (HttpOnly).
    """
    try:
        user_id = 1        
        # Si pasa la validación → conecta
        await ws_manager.connect(websocket,user_id)
        print(f"✅ Cliente WS conectado: usuario {user_id}")
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
                # await ws_manager.handle_message(websocket, data)
                # 5. Delegar la lógica de negocio al Dispatcher, pasando el objeto websocket
                await EventDispatcher.dispatch(websocket, message)
                
        except WebSocketDisconnect as e:
            print(f"❌ Cliente desconectado por {e}")
            ws_manager.disconnect(websocket)
            # _ = await websocket.receive_text()

    except Exception as e:
        print(f"❌ Error o desconexión WS: {e}")
        await websocket.close(code=1008)
