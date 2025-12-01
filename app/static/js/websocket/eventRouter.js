(function () {
  /**
   * Pattern: Observer / Publisher-Subscriber (Pub/Sub)
   * Function: Decouples WebSocket message reception (WebSocketClient)
   * from UI-specific logic (chat_handler.js).
   * Allows multiple UI components to subscribe to channels (e.g., 'chat')
   * or any type of events without knowing the sender.
 */
  class EventRouter {
    constructor() {
      this.channelHandlers = {}; // { 'chat': [fn1, fn2] } -> Handlers per channel (e.g: chat, notify, etc.)
      this.typeHandlers = {}; // { NEW_ORDER_MACHINE: [fn], ERROR_EVENT: [fn] } -> Handlers per event type
      this.globalHandlers = []; // Handlers for logging, debugging, or notifications
    }

     /**
       * Subscribe a callback function to a specific channel
       * @param {string} channel - The channel to subscribe to (e.g., 'chat')
       * @param {function} callback - Function to execute when message arrives
     */
    onChannel(channel, callback) {
      if (!this.channelHandlers[channel]) this.channelHandlers[channel] = [];
        this.channelHandlers[channel].push(callback);
    }

    /**
     * Subscribe a callback function to a specific type of message
     * @param {string} type - Event type to subscribe to
     * @param {function} callback - Function to execute when event occurs
   */
    onType(type, callback) {
      if (!this.typeHandlers[type]) this.typeHandlers[type] = [];
          this.typeHandlers[type].push(callback);
    }

    /**
     * Subscribe a callback to all messages (global handler)
     * Useful for logging or debugging
     * @param {function} callback 
   */
    onAll(callback) {
      this.globalHandlers.push(callback);
    }

    /**
     * Dispatches an incoming message to all relevant subscribers
     * @param {Object} message - Normalized message from WebSocketManager
   */
    dispatch(message) {
      try {
        const { channel, type } = message;

        if (this.globalHandlers.length)
          this.globalHandlers.forEach(cb => cb(message));

        // Execute channel-specific handlers
        if (channel && this.channelHandlers[channel])
          this.channelHandlers[channel].forEach(cb => cb(message));

        // Execute type-specific handlers
        if (type && this.typeHandlers[type])
          this.typeHandlers[type].forEach(cb => cb(message));
        
      } catch (err) {
        console.error("Error in dispatch:", err);
      }
    }
  }

  window.EventRouter = EventRouter;
})();
