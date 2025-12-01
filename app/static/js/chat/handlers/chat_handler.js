console.log("script cargado y ejecutándose");
(function () {
  function handleChatMessage(msg) {
    console.log("📦CHAT Message:", msg);

    switch (msg.type) {
      case "USER_NEW_MESSAGE":
        renderNewMessage(msg.payload);
        break;
      case "AI_MESSAGE":
        console.log('Entro en esta parte')
        renderNewMessage(msg.payload);
        break;
      default:
        console.log("CHAT mensaje no manejado:", msg.type);
    }
  }

  async function renderNewMessage(payload) {
      const chatBox = document.getElementById("messages");

      // Buscamos el último div de IA con puntos
      const aiDiv = chatBox.querySelector(".ai-message:last-child");
      if (!aiDiv) return;

      aiDiv.innerHTML = `
          <div class="fade-in" style="display: flex; align-items: center;">
              <img src="/assets/img/favicons/192c.png" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
              <span>${payload.text}</span>
          </div>
      `;

      chatBox.scrollTop = chatBox.scrollHeight;
  }

  window.initChatHandlers = function () {
    window.WebSocketManager.onChannel("chat", handleChatMessage);
  };
})();
