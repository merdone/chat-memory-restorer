import sqlite3

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("test.db")


    def __create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE chats
            (
                chat_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL 
            );
            """)

            cursor.execute("""
            CREATE TABLE messages
            (
                message_id INTEGER PRIMARY KEY,
                
            );
            """)
        self.connection.commit()