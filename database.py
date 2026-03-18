import sqlite3
import os

pathDB = './blog.db'

def get_db_connection():
    exist = os.path.exists(pathDB)
    conn = sqlite3.connect(pathDB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""--sql
        CREATE TABLE IF NOT EXISTS POSTS (
            ID INTEGER PRIMARY KEY,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published INTEGER DEFAULT 1,
            rating INTEGER
        )
    """)
    cursor = conn.execute("SELECT COUNT(*) FROM POSTS")
    if cursor.fetchone()[0] == 0:
        origin_query = ("INSERT INTO POSTS (author, title, content) VALUES (?, ?, ?)")
        conn.execute(origin_query, ('Tonhie', 'Origin', '醉酒当歌，人生几何？'))
        conn.commit()
    conn.close()