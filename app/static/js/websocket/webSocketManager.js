// clases/websockets/WebSocketManager.js
(function () {
    class WebSocketManager {
        constructor() {
            this.client = null;
            // this.subscribers = new Set();
            this.router = new EventRouter(); 
        }

        init(authToken,clientId) {
            if (this.client) return; // Ya inicializado

            this.client = new WebSocketClient(
                "/connect",
                authToken,
                // (data) => this.notifySubscribers(data),
                (data) => this.handleIncoming(data),
                (status, reconnecting, color) => this.handleStatus(status, reconnecting, color),
                clientId
            );

            this.client.connect();
        }

        handleIncoming(raw) {
            try {
                // Normalizamos el mensaje
                const normalized = {
                    channel: raw.channel, // o el canal global si no viene
                    type: raw.type || raw.event,
                    payload: raw.payload || raw.data || {},
                };
                console.log(normalized);
                // Despachamos al router
                this.router.dispatch(normalized);
            } catch (err) {
                console.error("❌ Error procesando mensaje WS:", err);
            }
        }

        handleStatus(status, reconnecting, color) {
            console.log(`[WS STATUS] ${status}`);
            // Aquí podrías actualizar un indicador global o disparar un evento UI
        }

        send(data) {
            if (this.client) this.client.send(data);
        }

        disconnect() {
            if (this.client) this.client.disconnect();
        }

        // API de conveniencia → redirige al router
        onChannel(channel, cb) { this.router.onChannel(channel, cb); }
        onType(type, cb) { this.router.onType(type, cb); }
        onAll(cb) { this.router.onAll(cb); }
    }

    //Creamos la instancia y exportamos globalmente
    const instance = new WebSocketManager();
    window.WebSocketManager = instance;
    // window.WebSocketManager = WebSocketManager
})();
// const wsManager = new WebSocketManager();

