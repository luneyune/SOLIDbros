import sqlite3

class DBManager:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
    
    def write_tenant(self, tg_id, tenant_id, phone_number):
        if not self.read_tenant(tg_id):
            self.cursor.execute("INSERT OR IGNORE INTO Users (tg_id, tenant_id, phone_number) VALUES (?, ?, ?)", (tg_id, tenant_id, phone_number))

        self.connection.commit()

    def read_tenant(self, tg_id):
        self.cursor.execute("SELECT tenant_id, phone_number FROM Users WHERE tg_id = ?",  (tg_id, ))
        return self.cursor.fetchone()
    
    def read_tenant_by_ten_id(self, tenant_id):
        self.cursor.execute("SELECT tg_id, phone_number FROM Users WHERE tenant_id = ?",  (tenant_id, ))
        return self.cursor.fetchone()
    
    def get_hashed_api_key(self):
        self.cursor.execute("SELECT x_api_key FROM TokenKeys")
        return self.cursor.fetchone()[0]

    def __del__(self):
        self.connection.close()