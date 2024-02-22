import sqlite3


class DBHandler:
    def __init__(self, db_name="mail_storage.db", table_name="emails"):
        self.db_name = db_name
        self.table_name = table_name
        self.table_schema = """(
                                    mail_id TEXT PRIMARY KEY,
                                    sender TEXT,
                                    receiver TEXT,
                                    mail_date INTEGER,
                                    subject TEXT
                                );"""
        self.conn = self.create_connection()
        self.create_table()

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.db_name)
            print(f"Connected to database: {self.db_name}")
            return conn
        except sqlite3.Error as e:
            print("Error connecting to Database:", e)

    def create_table(self):
        if self.conn is None:
            return

        try:
            cur = self.conn.cursor()
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table_name} {self.table_schema}"
            )
            self.conn.commit()
            if cur.rowcount > 0:
                print("Table created successfully")
        except sqlite3.Error as e:
            print("Error creating table", e)

    def insert_data(self, email_data):
        if self.conn is None:
            return
        try:
            insertStatment = f"""INSERT INTO {self.table_name} (mail_id, sender, receiver, mail_date, subject)
                VALUES (:mail_id, :sender, :receiver, :mail_date, :subject)"""
            cur = self.conn.cursor()
            cur.execute(insertStatment, email_data)
            self.conn.commit()
            print("Inserted Data Successfully")
        except sqlite3.Error as e:
            print("Error inserting data", e)

    def scan_table(self):
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM {self.table_name}")
            mail_data = cur.fetchall()
            return mail_data
        except sqlite3.Error as e:
            print("Error fetching data", e)

    def query_table(self, query_statment):
        try:
            query = f"SELECT * FROM {self.table_name} {query_statment}"
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            return rows
        except sqlite3.Error as e:
            print("Error querying  data", e)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Connection closed successfully")
