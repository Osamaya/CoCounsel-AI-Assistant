import asyncio
import logging
import random
from app.core.websocket.event_bus import event_bus
from app.core.websocket.event_dispatcher import EventDispatcher
from app.db.db_chat import *
logger = logging.getLogger(__name__)

# --- MOCK AI LOGIC (RULES-BASED) ---
def generate_mock_ai_response(user_text: str) -> str:
    """
        Generates a simulated response for a CoCounsel (Mock AI) using
        simple keyword-based rules and response templates.

        NOTE:
        The structure and ideas for this mock were inspired by AI-assisted (chatgpt)
        brainstorming, but the final implementation and domain adaptation
        were customized for this project.
    """
    text = user_text.lower().strip()
    
    rules = [
        ("hello", [
            "Hello! I'm your legal assistant. How can I help you today?",
            "Hi there! Do you need help with any legal documents or processes?"
        ]),
        ("bye", [
            "Goodbye 👋. If you have more legal questions, I’m here to help.",
            "See you later! Remember I can assist with any legal matters."
        ]),
        ("thank", [
            "You're welcome! Do you want me to explain something else about your case?",
            "No problem 😊. I'm here to assist with your legal questions."
        ]),
        ("contract", [
            "I can help you review the key points of your contract.",
            "Let's discuss your contract. Which part do you want to analyze?"
        ]),
        ("lawsuit", [
            "We can go over the initial steps of a lawsuit.",
            "I can explain the general process for filing a lawsuit."
        ]),
        ("law", [
            "I can explain what the law says about this matter.",
            "I can give you a summary of the legal rules that apply here."
        ]),
        ("registration", [
            "I can guide you on how to register a legal document.",
            "Let's go over the steps to correctly register your document."
        ]),
        ("property", [
            "I can help you with property and title inquiries.",
            "Are you asking about real estate or another type of property?"
        ]),
        ("will", [
            "I can explain the basics of writing a will.",
            "I can guide you on how to draft a valid will."
        ]),
        ("help", [
            "Sure! What legal matter do you need help with?",
            "I can provide guidance on your legal question. Please elaborate."
        ])
    ]

    for trigger, response in rules:
        if trigger in text:
            return random.choice(response)
        
    # Fallback response for unhandled input
    fallback_responses = [
        "Sorry, I didn t understand your query. Could you provide more details?",
        "I m not sure how to assist with that. Could you rephrase your question?",
        "This seems complex. Would you like me to guide you step by step?"
    ]
    
    return random.choice(fallback_responses)

# --- AI AGENT LOOP (The Consumer) ---
async def run_ai_agent():
    """
        The main Consumer loop. Runs indefinitely in the background (via lifespan).
    """
    logger.info("Agent initialized and awaiting...")
    
    while True:
        logger.info("Inside the agent's loop")
        
        # Block and consume event from the Event Bus (asyncio.Queue)
        event = await event_bus.consume_ai_event()
        
        try:
            client_id = event.get("client_id")
            user_text = event.get("text")
            
            # "Thinking"
            # Process: Simulate AI latency (key to proving asynchronicity)
            #We manage it within the front end.
            await asyncio.sleep(1.5) 
            
            response_text = generate_mock_ai_response(user_text)

            # Persistence: Save AI response to DB (Uses provided persistence functions)
            """I used SQLITE to make the persistence"""
            session_id = get_sessions_or_create(client_id)
            save_message(session_id, "ai", response_text)
            
            # Respond: Use the Event Dispatcher to send the directed message
            payload = {
                "channel" : "chat",
                "type": "AI_MESSAGE",
                "payload": {
                    "text": response_text,
                    "timestamp": "now" # Puedes poner datetime.now().isoformat()
                }
            }
            
            # The AI Agent emits a message back via the central Mediator/Dispatcher.
            await EventDispatcher.emit(payload,target_client=client_id)
            
        except Exception as e:
            logger.error(f"Error in AI Agent Loop: {e}")
        
        # Signal the queue that the task is complete
        event_bus.ai_queue.task_done()