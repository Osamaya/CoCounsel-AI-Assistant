console.log("script cargado y ejecutándose");
(function () {
  function handleChatMessage(msg) {
    console.log("📦CHAT Message:", msg);

    switch (msg.type) {
      case "USER_NEW_MESSAGE":
        renderNewMessage(msg.payload);
        break;
      case "AI_MESSAGE":
        renderNewMessage(msg.payload);
        break;
      default:
        console.log("CHAT mensaje no manejado:", msg.type);
    }
  }

  async function renderNewMessage(payload) {
      // Aquí actualizamos el DOM
      console.log(`LA IA NOS DICE ${payload}`)
    //   await drawMessage(payload)
  }

  window.initChatHandlers = function () {
    window.WebSocketManager.onChannel("chat", handleChatMessage);
  };
})();
