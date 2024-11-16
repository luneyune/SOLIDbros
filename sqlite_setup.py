import sqlite3


def db_setup():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                tg_id INTEGER,
                tenant_id INTEGER,
                phone_number TEXT
                )    
    ''')
    conn.commit()
    conn.close()