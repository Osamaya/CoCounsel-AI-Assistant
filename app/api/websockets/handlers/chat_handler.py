from fastapi import WebSocket
from app.core.websocket.event_dispatcher import EventDispatcher

# async def handle_notify_event(message: dict):
async def handle_chats_event(websocket: WebSocket, message: dict):
    print("🔔 Mensaje canal CHAT recibido:", message)

    tipo = message.get("type")
    payload = message.get("payload", {})

    if tipo == "NEW_USER_MESSAGE":
        user_text = payload.get("text")

        # 1. Persistencia mock
        print("💾 Guardando mensaje:", user_text)
        #  2. Respuesta MOCK IA (por ahora)
        ai_response = f"🤖 Respuesta simulada a: '{user_text}'"

        # 3. Emitir respuesta al chat
        await EventDispatcher.emit({
            "channel": "chat",
            "type": "AI_MESSAGE",
            "payload": {
                "text": ai_response,
                "timestamp": "2025-11-26T12:00:00"
            }
        })

    elif tipo == "SYSTEM":
        print(f"📘 Notificación marcada como leída: {payload}")

    else:
        print(f"⚠️ Tipo de evento no manejado: {tipo}")
