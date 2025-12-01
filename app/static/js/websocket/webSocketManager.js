(function () {
    /**
         * Pattern: Facade / Singleton
         * Acts as the public interface for the frontend (chat.js)
         * Initializes EventRouter (Mediator) and WebSocketClient (Network)
         * and normalizes messages before dispatching.
         * Allows frontend modules to subscribe to events without creating multiple WS connections.
     */
    class WebSocketManager {
        constructor() {
            this.client = null;
            this.router = new EventRouter(); // Mediator for UI event handlers
        }

        /**
         * Initialize WebSocket client and connect
         * @param {string} clientId - Client ID for session
         */
        init(clientId) {
            if (this.client) return; // Aseguramos el Singleton

            this.client = new WebSocketClient(
                "/connect", // Endpoint WS
                (data) => this.handleIncoming(data), // Callback para mensajes recibidos
                (status, reconnecting, color) => this.handleStatus(status, reconnecting, color),
                clientId // ID de sesión generado en el cliente
            );

            this.client.connect();
        }

        handleIncoming(raw) {
            try {
                /**
                 *  Normalize incoming messages and dispatch to router -> 'channel', 'type' y 'payload'. 
                 * @param {Object} raw - Object that contains the response from our backend.
                 */
                const normalized = {
                    channel: raw.channel,
                    type: raw.type || raw.event,
                    payload: raw.payload || raw.data || {},
                };
                // Despachamos al router para que los Handlers suscritos reaccionen.
                this.router.dispatch(normalized);
            } catch (err) {
                console.error("Error processing WS message:", err);
            }
        }

        /** Handle connection status updates */
        handleStatus(status, reconnecting, color) {
            console.log(`[WS STATUS] ${status}`);
        }

         /** Send message to WebSocket server */
        send(data) {
            if (this.client) this.client.send(data);
        }

        /** Disconnect WebSocket client */
        disconnect() {
            if (this.client) this.client.disconnect();
        }

        // Convenience methods for frontend subscriptions
        onChannel(channel, cb) { this.router.onChannel(channel, cb); }
        onType(type, cb) { this.router.onType(type, cb); }
        onAll(cb) { this.router.onAll(cb); }
    }

    // Create singleton instance
    const instance = new WebSocketManager();
    window.WebSocketManager = instance;
})();

