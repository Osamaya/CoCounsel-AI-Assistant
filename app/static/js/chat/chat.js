/**
    * Initialize WebSocket connection immediately on script load
 */
(async()=>{
    await initWebSocket();
})()

/**
 * Ensures a persistent session ID (client_id).
 * This ID is used by the backend (WebSocketManager) to map connections.
 * @returns {string} UUID of the client
 */
function getOrCreateClientId() {
    let clientId = localStorage.getItem("client_id");
    if (!clientId) {
        clientId = crypto.randomUUID();
        localStorage.setItem("client_id", clientId);
    }
    return clientId;
}

/**
 * Main function to initialize WebSocket.
 * Steps:
 * 1. Get or create client_id
 * 2. Initialize WebSocketManager with the client ID
 * 3. Initialize chat handlers (subscribe to 'chat' channel)
 * 4. Load previous chat messages from backend
 */
async function initWebSocket()
{
    try {
        const clientId = getOrCreateClientId();
        await window.WebSocketManager.init(clientId); // Connect WS
        window.initChatHandlers();  // Subscribe to chat channel
        await getChatMessaes(clientId); // Load chat history
    } catch (error) {
        console.error(`Unable to establish WebSocket connection: ${error}`);
        throw new Error(error);
    }
}

/**
     * Sends user message to the backend via WebSocket
     * Steps:
     * 1. Render user message in the DOM
     * 2. Render placeholder "Typing..." for AI response
     * 3. Emit the event through WebSocketManager
 */
function sendMessage() {
    let message = document.getElementById("user-message").value;
    if (!message.trim()) return;

    const chatBox = document.getElementById("messages");
    
    // Render user message
    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = message;
    chatBox.appendChild(userMessage);

    document.getElementById("user-message").value = "";

    // Render AI typing "typing dots"
    const botContainer = document.createElement("div");
    botContainer.className = "ai-message";
    botContainer.innerHTML = `
        <div style="display: flex; align-items: center;">
            <img id="bot-avatar" src="/static/assets/logo/tr.png" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
            <span id="typing-dots">Thinking<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>
        </div>
    `;
    chatBox.appendChild(botContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send message to backend via WebSocket
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

/**
     * Fetches chat history for a given client_id from backend
     * @param {string} clientId - Client ID stored in localStorage
 */
async function getChatMessaes(clientId)
{
    const response = await fetch(`http://localhost:8000/ws/get-messages-user/${clientId}`, {
        method: "GET",
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
    });
    let respuesta = await response.json();
    renderChatHistory(respuesta.messages)
}

/**
 * Renders chat history in the DOM
 * @param {Array} messages - Array of message objects {sender, content, created_at}
 */
async function renderChatHistory(messages) {
    const chatBox = document.getElementById("messages");
    
    // Clear previous messages
    chatBox.innerHTML = "";

    for (const msg of messages) {
        const msgDiv = document.createElement("div");

        // Clase dependiendo del remitente
        msgDiv.className = msg.sender === "user" ? "user-message" : "ai-message fade-in";

        // Contenido
        if (msg.sender === "ai") {
            msgDiv.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <img src="/static/assets/logo/tr.png" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
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


// Event listener: send message on ENTER key
const inputField = document.getElementById("user-message");
inputField.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Evita saltos de línea
        sendMessage();
    }
});
