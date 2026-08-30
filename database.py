import sqlite3


class Database:
    def __init__(self, database_path):
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("""PRAGMA foreign_keys = ON""")
        self.__create_tables()

    def __create_tables(self):
        with self._connection:
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS chats
                (
                    chat_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL 
                );
                """)

            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS media_files
                (
                    source_sha256 TEXT PRIMARY KEY NOT NULL,
                    path TEXT NOT NULL
                );
            """)

            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS messages
                (
                    message_id INTEGER NOT NULL,
                    media_type TEXT NOT NULL,
                    source_sha256 TEXT NOT NULL,
                    media_date TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    
                    PRIMARY KEY (chat_id, message_id),
                    
                    FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                    FOREIGN KEY (source_sha256) REFERENCES media_files(source_sha256)
                );
                """)

    def add_chat(self, chat_id, name):
        with self._connection:
            sql_command = """INSERT INTO chats (chat_id, name) 
                        VALUES (?, ?)
                        ON CONFLICT (chat_id)
                        DO UPDATE SET name = excluded.name;
                        """
            self._connection.execute(sql_command, (chat_id, name))

    def add_message(self, message_id, media_type, source_sha256, media_date, chat_id):
        with self._connection:
            sql_command = """INSERT INTO messages (message_id, media_type, source_sha256, media_date, chat_id)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT (chat_id, message_id) DO NOTHING;"""
            self._connection.execute(sql_command, (message_id, media_type, source_sha256, media_date, chat_id))

    def search_max_message_id(self, chat_id):
        sql_command = """SELECT MAX(message_id) FROM messages WHERE chat_id = ?"""
        sql_result = self._connection.execute(sql_command, (chat_id,))
        input_result = dict(sql_result.fetchone())
        return input_result.get("MAX(message_id)", 0)

    # in each situation returns path of the file
    def get_or_add_media_file(self, source_sha256, path):
        search_result = self.get_media_file_by_hash(source_sha256)
        if search_result is not None:
            return search_result
        with self._connection:
            sql_command = """INSERT INTO media_files (source_sha256, path) VALUES (?, ?)"""
            self._connection.execute(sql_command, (source_sha256, path))
        return path

    def get_media_file_by_hash(self, source_sha256):
        sql_command = """SELECT * FROM media_files WHERE source_sha256 = ?"""
        sql_result = self._connection.execute(sql_command, (source_sha256,))
        input_result = sql_result.fetchone()
        if input_result:
            input_dict = dict(input_result)
            return input_dict["path"]
        return None

    def close(self):
        self._connection.close()
