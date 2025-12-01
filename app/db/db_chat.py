import sqlite3
DB_PATH = "app/db/chat.db"

def get_db():
    return sqlite3.connect(DB_PATH)

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.executescript("""
#         CREATE TABLE IF NOT EXISTS session_chat (
#             id_session INTEGER PRIMARY KEY AUTOINCREMENT,
#             sc_client_id TEXT NOT NULL,
#             sc_created_at TEXT DEFAULT (datetime('now')),
#             sc_status TEXT DEFAULT 'active'
#         );

#         CREATE TABLE IF NOT EXISTS messages_chat (
#             id_message INTEGER PRIMARY KEY AUTOINCREMENT,
#             mc_id_session INTEGER NOT NULL,
#             mc_sender TEXT NOT NULL,
#             mc_content TEXT NOT NULL,
#             mc_created_at TEXT DEFAULT (datetime('now')),
#             FOREIGN KEY (mc_id_session) REFERENCES session_chat(id_session) ON DELETE CASCADE
#         );
#     """)
#     conn.commit()
#     conn.close()

# # ---Funciones auxiliares ---
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
        cursor.execute("""INSERT 
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

def save_message(session_id: int, sender: str, content: str):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
            """
                INSERT INTO messages_chat 
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
