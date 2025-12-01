  /**
  * Chat Event Handler (Consumer of EventRouter)
  * Purpose: Reacts to incoming messages on 'chat' channel and updates DOM
 */
(function () {

  /**
     * Handles messages from the 'chat' channel
     * @param {Object} msg - Incoming WS message object
    */
  function handleChatMessage(msg) {
   
    //The switch-case redirects the event to the specific render function.
    switch (msg.type) {
      case "AI_MESSAGE":
        renderNewMessage(msg.payload);
        break;
      default:
        console.log("CHAT unmanaged message:", msg.type);
    }
  }

  /**
     * Renders AI response in the chat
     * Replaces the "Thinking..." placeholder with actual AI message
     * @param {Object} payload - Message payload containing `text`
  */
  async function renderNewMessage(payload) {
      const chatBox = document.getElementById("messages");

      // Buscamos el último div de IA con puntos
      const aiDiv = chatBox.querySelector(".ai-message:last-child");
      if (!aiDiv) return;

      aiDiv.innerHTML = `
          <div class="fade-in" style="display: flex; align-items: center;">
              <img src="/static/assets/logo/tr.png" alt="Bot" style="width: 30px; height: 30px; margin-right: 8px;">
              <span>${payload.text}</span>
          </div>
      `;

      chatBox.scrollTop = chatBox.scrollHeight;
  }

  /**
    * Expose the subscription point
    * Registers handler to 'chat' channel in EventRouter
  */
  window.initChatHandlers = function () {
    window.WebSocketManager.onChannel("chat", handleChatMessage);
  };
})();
