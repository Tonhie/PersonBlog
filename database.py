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
    conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS POSTS (
            ID INTEGER PRIMARY KEY,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published INTEGER DEFAULT 1,
            rating INTEGER,
            level TEXT DEFAULT 'INFO',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        conn.execute("ALTER TABLE POSTS ADD COLUMN level TEXT DEFAULT 'INFO'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE POSTS ADD COLUMN created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))")
    except sqlite3.OperationalError:
        pass

    conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS COMMENTS (
            id INTEGER PRIMARY KEY,
            post_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            ip_address TEXT,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (post_id) REFERENCES POSTS (ID)
        )
    ''')

    conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS SYS_LOGS (
            id INTEGER PRIMARY KEY,
            ip_address TEXT,
            env_key TEXT NOT NULL,
            env_val TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor = conn.execute("SELECT COUNT(*) FROM POSTS")
    if cursor.fetchone()[0] == 0:
        origin_query = ("INSERT INTO POSTS (author, title, content, level) VALUES (?, ?, ?, ?)")                                                                                  
        conn.execute(origin_query, ('Tonhie', 'Origin', '对酒当歌，人生几何？', 'INFO'))
        conn.commit()
    conn.close()
