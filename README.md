# Real-Time CoCounsel-AI-Assistant (Event-Driven Architecture)
This project is a real-time AI-powered chat system built with FastAPI and WebSockets using an event-driven asynchronous architecture. It simulates a legal AI assistant ("CoCounsel") using a mock AI engine with structured conversational rules.

The architectural design of this project is based on experience gained from real-world production systems and follows scalable and decoupled software design principles.

---

## Overview

This system demonstrates:
- Full-duplex real-time communication using WebSockets.
- Internal Event Bus implementation  without external brokers (Kafka/Redis).
- Asynchronous AI Agent loop.
- SQLite-based persistence.
- Modular backend architecture.
- Decoupled frontend using native JavaScript.

It is designed for technical evaluation, architectural demonstration, and interview defense.

---
## Project Structure Overview
app/
│ main.py
│ init.py
│
├── api/
│ └── websockets/
│ ├── ws_routes.py
│ └── handlers/
│ └── chat_handler.py
│
├── core/
│ └── websocket/
│ ├── event_bus.py
│ ├── event_dispatcher.py
│ ├── init_dispatchers.py
│ ├── ws_manager.py
│
├── db/
│ ├── chat.db
│ └── db_chat.py
│
├── models/
│
├── services/
│ └── ai_agent.py
│
└── static/
├── index.html
├── css/
│ └── chat.css
├── assets/
│ ├── icon/
│ └── logo/
└── js/
├── chat/
│ ├── chat.js
│ └── handlers/
│ └── chat_handler.js
└── websocket/
├── eventRouter.js
├── webClientClass.js
└── webSocketManager.js
---

# INSTALLATION & RUNNING THE PROJECT (WITH uv)
This project uses **uv** for fast Python dependency and environment management.

### 1. Install uv (if not installed)
pip install uv

### 2. Create virtual environment
uv venv

### 3. Activate 
source .venv/Scripts/activate

### 4. Install all project dependencies
uv sync

### 5. RUN
uvicorn app.main:app --reload

### 6. OPEN
http://localhost:8000/

---

## Tech Stack
- Python 3.13
- FastAPI
- WebSockets
- SQLite
- AsyncIO
- HTML / CSS / JavaScript
- uv (for Python environment and dependency management)

---

## Example Prompts to Test the Mock AI

You can test the AI behavior using the following example messages:

- hello
- bye
- thank you
- contract
- lawsuit
- law
- registration
- property
- will
- help

---

## WebSocket Flow

1. Client connects to the WebSocket endpoint.
2. Client sends a `NEW_USER_MESSAGE` event.
3. The message is routed via the `EventDispatcher`.
4. The `ChatHandler` publishes the event into the `EventBus`.
5. The `AI Agent` consumes the event asynchronously.
6. The mock AI processes the message.
7. The response is persisted in SQLite.
8. The AI response is sent back only to the originating client.

---

## Event Bus

The Event Bus is implemented using `asyncio.Queue` and acts as an internal message broker.  
It allows the system to decouple:
- Message reception
- AI processing
- WebSocket response delivery

This simulates how real distributed systems operate without using Kafka, Rabbit, etc.

---

## AI Agent Loop

The AI Agent runs as a background coroutine:
- Waits for incoming events.
- Applies a rule-based mock AI engine.
- Simulates processing delay.
- Persists messages.
- Sends final responses through the WebSocket Manager.

The mock AI logic was designed with legal conversational patterns in mind (CoCounsel concept).

---

## SQLite Persistence

The system stores:
- Chat sessions
- Chat messages (user and AI)

This ensures message traceability and state recovery during testing.


### Tables:
---
**session_chat** 
Stores chat sessions per client:

Column	        Description
id_session	    Primary key
sc_client_id	UUID per browser
sc_status	    active/closed
sc_created_at	timestamp
---
**messages_chat**
Stores user's + AI history:

Column	        Description
id_message	    Primary key
mc_id_session	FK to session_chat
mc_sender	    user / ai
mc_content	    message text
mc_created_at	timestamp
---

### UI Design Notes
The project uses a Thomson Reuters–inspired color palette, including:

Color	         Example Use
#d64000	    Primary accent
#00b7c2;       button

## License & Disclaimers

**The project is educational and non-commercial.*
**The main logo of the project was generated using AI-based image generation tools strictly for educational and demo purposes.*
**A Thomson logo and the color pallette are used strictly as a UI simulation asset in a non-commercial academic context. All rights belong to their respective owners.*

AI tools were used as support for:
-Comment validation
-Mock AI response design
-Documentation assistance

This project is not affiliated with any commercial entity.

All intellectual property belongs to their respective owners.
---
