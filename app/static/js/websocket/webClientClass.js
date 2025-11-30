 // --- CLASE GENÉRICA PARA EL MANEJO DE WEBSOCKETS (Lógica de Red) ---
(function () {
    class WebSocketClient {
        /**
         * Cliente genérico de WebSocket con lógica de reconexión y manejo de errores.
         * @param {string} endpoint - La sub-ruta del WS (ej: '/trazabilidad').
         * @param {string} authToken - El token JWT para autenticación (se envía en el query param).
         * @param {function} onDataReceived - Callback para manejar mensajes de datos recibidos (Lógica de UI).
         * @param {function} onStatusChange - Callback para notificar cambios de estado (Lógica de UI).
         */
        constructor(endpoint, authToken, onDataReceived, onStatusChange) {
            // Aquí se adjunta el token JWT para la validación en el Back-End
            this.url = `ws://localhost:8000/ws${endpoint}`;
            this.onDataReceived = onDataReceived;
            this.onStatusChange = onStatusChange;
            this.socket = null;
            this.reconnectTimeout = null;
            this.MAX_RETRY_DELAY = 16000;
            this.currentRetryDelay = 1000;
        }

        connect() {
            if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
            
            this.onStatusChange?.("Conectando...", true, 'yellow');
            this.socket = new WebSocket(this.url);

            this.socket.onopen = this.handleOpen.bind(this);
            this.socket.onmessage = this.handleMessage.bind(this);
            this.socket.onerror = this.handleError.bind(this);
            this.socket.onclose = this.handleClose.bind(this);
        }

        handleOpen(e) {
            console.log("[WS Client] Conexión establecida:", this.url);
            this.currentRetryDelay = 1000; 
            this.onStatusChange("Conectado", false, 'green');
        }

        handleMessage(event) {
            try {
                const data = JSON.parse(event.data);
                // Llama al callback específico de la UI
                this.onDataReceived?.(data); 
            } catch (e) {
                console.error("Error al parsear el mensaje JSON:", e, event.data);
            }
        }

        handleError(error) {
            console.error(`[WS Client] Error de WebSocket:`, error);
            this.onStatusChange("Error", true, 'red');
        }

        handleClose(event) {
            if (!event.wasClean) {
                // Si la conexión se cierra inesperadamente, intenta reconectar con backoff
                console.warn('[WS Client] Conexión rota. Intentando reconectar...');
                this.onStatusChange("Reconectando...", true, 'orange');
                
                this.reconnectTimeout = setTimeout(() => {
                    this.connect();
                    this.currentRetryDelay = Math.min(this.MAX_RETRY_DELAY, this.currentRetryDelay * 2);
                }, this.currentRetryDelay); 
                
            } else {
                // Cierre limpio
                this.onStatusChange("Desconectado", false, 'red');
            }
        }

        disconnect() {
            if (this.socket) {
                this.socket.close(1000, "Cierre manual por el usuario");
                if (this.reconnectTimeout) {
                        clearTimeout(this.reconnectTimeout);
                }
            }
        }

        send(data) {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify(data));
            } else {
                console.warn("[WS] No se puede enviar: conexión no abierta");
            }
        }
    }
    window.WebSocketClient = WebSocketClient;
})()
// --- FIN DE LA CLASE GENÉRICA ---