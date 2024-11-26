import sqlite3

class database():

    def __init__(self):
        # Define our database name
        self.DBname = 'toka_db.db'

    def connect(self):
        # Creates our database connection
        conn = None
        try:
            conn = sqlite3.connect(self.DBname)
        except Exception as e:
            print(f"An error occurred: {e}")
        return conn

    def disconnect(self, conn):
        # Closes our database connection
        if conn:
            conn.close()

    def queryDB(self, command, params=[]):
        """
        Execute SELECT queries
        """
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(command, params)
        result = cur.fetchall()
        self.disconnect(conn)
        return result

    def modifyDB(self, command, params=[]):
        """
        Execute INSERT, UPDATE, DELETE queries
        """
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(command, params)
            conn.commit()  # Commit the changes
            result = cur.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()  # Rollback if any error occurs
            result = []
        finally:
            self.disconnect(conn)
        return result