import sqlite3

class database():

    def __init__(self):
        # Define our database FlaskPracticeDB.db
        self.DBname = 'toka_db.db'

    def connect(self):
        # Creates our database connection
        conn = None
        try:
            conn = sqlite3.connect(self.DBname)
        except Exception as e:
            print(f"An error occured: {e}")
        return conn

    def disconnect(self, conn):
        # Closes our database
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
        # try:
        #     cur.execute(command, params)F
        #     conn.commit()  # Commit the changes
        #     result = cur.fetchall()
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     conn.rollback()  # Rollback if any error occurs
        # finally:
        cur.execute(command, params)
        conn.commit()
        result = cur.fetchall()
        
        self.disconnect(conn)
        return result