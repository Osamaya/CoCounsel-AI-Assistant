// EventRouter.js
(function () {
  class EventRouter {
    constructor() {
      this.channelHandlers = {}; // { rf: [fn, fn], coating: [fn] }
      this.typeHandlers = {}; // { NEW_ORDER_MACHINE: [fn], ERROR_EVENT: [fn] }
      this.globalHandlers = []; // para logs, debug o notificaciones
    }

    onChannel(channel, callback) {
      if (!this.channelHandlers[channel]) this.channelHandlers[channel] = [];
        this.channelHandlers[channel].push(callback);
    }

    onType(type, callback) {
      if (!this.typeHandlers[type]) this.typeHandlers[type] = [];
        this.typeHandlers[type].push(callback);
    }

    onAll(callback) {
      this.globalHandlers.push(callback);
    }

    dispatch(message) {
      try {
        const { channel, type } = message;

        if (this.globalHandlers.length)
          this.globalHandlers.forEach(cb => cb(message));

        if (channel && this.channelHandlers[channel])
          this.channelHandlers[channel].forEach(cb => cb(message));

        if (type && this.typeHandlers[type])
          this.typeHandlers[type].forEach(cb => cb(message));
      } catch (err) {
        console.error("Error en dispatch:", err);
      }
    }
  }

  window.EventRouter = EventRouter;
})();
