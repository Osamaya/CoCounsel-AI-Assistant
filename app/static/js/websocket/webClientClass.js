/**
     * Generic WebSocket client with reconnection and error handling logic.
     * Handles connection lifecycle and delegates received messages to UI callbacks.
 */
(function () {
    class WebSocketClient {
        /**
         * Cliente genérico de WebSocket con lógica de reconexión y manejo de errores.
         * @param {string} endpoint -  WS sub-path (e.g., '/connect')
         * @param {string} clientId - ClientI generated for the user sessions.
         * @param {function} onDataReceived - Callback for incoming data (UI Logic).
         * @param {function} onStatusChange - Callback for connection status updates (UI Logic).
         */
        constructor(endpoint,onDataReceived, onStatusChange,clientId) {
            // Formamos la URL con el client_id para mantener la sesión.
            this.url = `ws://localhost:8000/ws${endpoint}?client_id=${clientId}`;
            this.onDataReceived = onDataReceived;
            this.onStatusChange = onStatusChange;
            this.socket = null;
            this.reconnectTimeout = null;
            this.MAX_RETRY_DELAY = 16000; // Max backoff delay
            this.currentRetryDelay = 1000; // Initial backoff delay
        }
        // Connect to WebSocket server  https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket
        connect() {
            if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
            
            this.onStatusChange?.("Connecting...", true, 'yellow');
            this.socket = new WebSocket(this.url);

            this.socket.onopen = this.handleOpen.bind(this);
            this.socket.onmessage = this.handleMessage.bind(this);
            this.socket.onerror = this.handleError.bind(this);
            this.socket.onclose = this.handleClose.bind(this);
        }
        
        /** Called when WebSocket connection is established */
        handleOpen(e) {
            console.log("[WS Client] Connection established:", this.url);
            this.currentRetryDelay = 1000; 
            this.onStatusChange("Connected", false, 'green');
        }

        /** Handles incoming messages from WebSocket */
        handleMessage(event) {
            try {
                const data = JSON.parse(event.data);
                // Llama al callback específico de la UI
                this.onDataReceived?.(data); 
            } catch (e) {
                console.error("Error parsing JSON message:", e, event.data);
            }
        }

        /** Called on WebSocket error */
        handleError(error) {
            console.error(`[WS Client] WebSocket error:`, error);
            this.onStatusChange("Error", true, 'red');
        }

        /**
         * Handles connection close and reconnection logic
         * exponential backoff strategy.
         * If the connection closes unexpectely (event.wasClean is false),
         * it waits twice as long as last time to reconnect.
         */
        handleClose(event) {
            if (!event.wasClean) {
                // Si la conexión se cierra inesperadamente, intenta reconectar con backoff
                console.warn("[WS Client] Connection lost, attempting to reconnect...");
                this.onStatusChange("Reconnecting...", true, 'orange');
                
                this.reconnectTimeout = setTimeout(() => {
                    this.connect();
                    this.currentRetryDelay = Math.min(this.MAX_RETRY_DELAY, this.currentRetryDelay * 2);
                }, this.currentRetryDelay); 
                
            } else {
                // Clean closed (manual)
                this.onStatusChange("Disconnected", false, 'red');
            }
        }

        disconnect() {
            if (this.socket) {
                this.socket.close(1000, "Manual disconnect");
                if (this.reconnectTimeout) {
                        clearTimeout(this.reconnectTimeout);
                }
            }
        }
        /** Send data to WebSocket server */
        send(data) {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify(data));
            } else {
                console.warn("[WS] Cannot send: connection not open");
            }
        }
    }
    window.WebSocketClient = WebSocketClient;
})()
// --- FIN DE LA CLASE ---