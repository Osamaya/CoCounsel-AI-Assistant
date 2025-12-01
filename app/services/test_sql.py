# test_db.py
import sqlite3
from app.db.db_chat import DB_PATH
def test():
    # # Crear la DB y tablas si no existen
    # init_db()
    
    # # Conectamos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Listar todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tablas en la DB:", tables)

    # Ver contenido (aunque estará vacío si no has insertado nada)
    cursor.execute("SELECT * FROM session_chat;")
    print("Contenido session_chat:", cursor.fetchall())

    cursor.execute("SELECT * FROM messages_chat;")
    print("Contenido messages_chat:", cursor.fetchall())

    conn.close()
    
if __name__ == "__main__":
    test()