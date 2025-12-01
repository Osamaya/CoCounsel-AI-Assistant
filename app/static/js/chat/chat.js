async function getChatMessaes(clientId)
{
    const response = await fetch(`http://localhost:8000/ws/get-messages-user/${clientId}`, {
        method: "GET",
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        // body: JSON.stringify(record)
    });
    let respuesta = await response.json();
    renderChatHistory(respuesta.messages)
}

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


function getOrCreateClientId() {
    let clientId = localStorage.getItem("client_id");
    if (!clientId) {
        clientId = crypto.randomUUID();
        localStorage.setItem("client_id", clientId);
    }
    return clientId;
}

/**Iniciamos la conexión a websockets y los handlers de eventos del chat */
async function initWebSocket()
{
    try {
        /**Creamos aparte la instancia de nuestro websocket con el backend */
        const clientId = getOrCreateClientId();
        console.log(`Soy el cliente id ${clientId}`)
        await window.WebSocketManager.init(null,clientId);
        window.initChatHandlers()
        await getChatMessaes(clientId)
        // Suscripción global para logs o debug
    } catch (error) {
        console.error(`No se pudo establecer conexión ${error}`)
        throw new Error(error);
    }
}

(async()=>{
    await initWebSocket();
})()


async function renderChatHistory(messages) {
    const chatBox = document.getElementById("messages");
    
    // Limpiamos cualquier mensaje previo
    chatBox.innerHTML = "";

    for (const msg of messages) {
        const msgDiv = document.createElement("div");

        // Clase dependiendo del remitente
        msgDiv.className = msg.sender === "user" ? "user-message" : "ai-message fade-in";

        // Contenido
        if (msg.sender === "ai") {
            msgDiv.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <img src="/assets/img/favicons/192c.png" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
                    <span>${msg.content}</span>
                </div>
            `;
        } else {
            msgDiv.textContent = msg.content;
        }

        chatBox.appendChild(msgDiv);

        // Scroll al final
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}


//Eventos
const inputField = document.getElementById("user-message");
inputField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Evita saltos de línea
        sendMessage();
    }
});
