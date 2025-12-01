import sqlite3
DB_PATH = "app/db/chat.db"

def get_db():
    """Return a SQLite connection object."""
    return sqlite3.connect(DB_PATH)

"""Get an active session for a client or create one if it doesn't exist."""
def get_sessions_or_create(client_id: str) -> int:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
                    SELECT id_session 
                    FROM session_chat 
                    WHERE sc_client_id = ? AND sc_status = 'active'
                    """,(
                            client_id,
                        )
                    )
    row = cursor.fetchone()
    
    if row:
        session_id = row[0]
    else:
        cursor.execute("""
                        INSERT 
                            INTO session_chat (sc_client_id) 
                            VALUES (?)
                        """,(
                                client_id,
                            )
                    )
        session_id = cursor.lastrowid
        db.commit()
    
    db.close()
    return session_id

"""Save a message in the database for a given session.
    Parameters:
    - session_id (int): ID of the chat session.
    - sender (str): 'user' or 'ai' indicating who sent the message.
    - content (str): The text content of the message.
"""
def save_message(session_id: int, sender: str, content: str):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
            """
                INSERT 
                    INTO messages_chat 
                    (
                        mc_id_session, 
                        mc_sender, 
                        mc_content
                    ) VALUES (?, ?, ?)"""
                    ,
                    (
                        session_id, 
                        sender, 
                        content
                    )
    )
    db.commit()
    db.close()
    
"""
    Retrieve all messages for the active session of a given client.
    
    Parameters:
    - client_id (str): Unique identifier of the client.
    
    Returns:
    - dict: {"messages": [{"sender": str, "content": str, "created_at": str}, ...]}
            An empty list if no active session exists.
"""
def get_user_messages(client_id : str):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id_session 
        FROM session_chat
        WHERE sc_client_id = ? AND sc_status = 'active'
    """, (client_id,))
    session = cursor.fetchone()
    if not session:
        return {"messages": []}
    
    session_id = session[0]
    
    cursor.execute("""
        SELECT mc_sender, mc_content, mc_created_at
        FROM messages_chat
        WHERE mc_id_session = ?
        ORDER BY mc_created_at ASC
    """, (session_id,))
    
    messages = [
        {"sender": row[0], "content": row[1], "created_at": row[2]}
        for row in cursor.fetchall()
    ]
    db.close()
    
    return {"messages": messages}
