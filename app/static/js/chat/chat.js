function sendMessage() {
    let message = document.getElementById("user-message").value;
    if (!message.trim()) return;

    const chatBox = document.getElementById("messages");
    const currentPath = window.location.pathname;
    const basePath = currentPath.split('/').slice(0, 2).join('/');
    const iconoXo = `${basePath}/assets/img/favicons/192c.png`;

    // Mensaje del usuario
    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = message;
    chatBox.appendChild(userMessage);

    document.getElementById("user-message").value = "";

    // Contenedor del bot con "typing dots"
    const botContainer = document.createElement("div");
    botContainer.className = "ai-message";
    botContainer.innerHTML = `
        <div style="display: flex; align-items: center;">
            <img id="bot-avatar" src="${iconoXo}" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
            <span id="typing-dots">Escribiendo<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>
        </div>
    `;
    chatBox.appendChild(botContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    // EMITIMOS EL EVENTO AL BACK POR WS 
    window.WebSocketManager.send({
        channel: "chat",
        type: "NEW_USER_MESSAGE",
        payload: {
            text: message,
            user_id: 1 || 2,
            timestamp: new Date().toISOString()
        }
    });
}


async function initWebSocket()
{
    try {
        /**Creamos aparte la instancia de nuestro websocket con el backend */
        await window.WebSocketManager.init(null);
        window.initChatHandlers()
        // Suscripción global para logs o debug
    } catch (error) {
        console.error(`No se pudo establecer conexión ${error}`)
        throw new Error(error);
    }
}

(async()=>{
    await initWebSocket();
})()



