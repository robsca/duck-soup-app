# import the sqlite3 module
import sqlite3

class database:
    def __init__(self, name):
        self.name = name
        # create a connection to the database
        try:
            self.conn = sqlite3.connect(self.name)
            self.cursor = self.conn.cursor()
        except:
            print("Error connecting to database")
            print('You might need to create the database first')

    def create_table(self):
        self.cursor.execute("CREATE TABLE notes (title TEXT, text TEXT, date TEXT, tags TEXT)")

    def new_note(self,title,text,date,tags):
        # title need to be unique check it first
        self.cursor.execute("SELECT * FROM notes WHERE title=?", (title,))
        note = self.cursor.fetchone()
        if note:
            print("Note already exists")
            return False
        else:
            # create a new note
            self.cursor.execute("INSERT INTO notes VALUES (?, ?, ?, ?)", (title, text, date, tags))
            # commit the changes
            self.conn.commit()
            return True

    def get_all_notes(self):
        # try to open the notes table
        self.cursor.execute("SELECT * FROM notes")
        notes = self.cursor.fetchall()
        return notes

    def get_single_note(self, title):
        # get a single note
        self.cursor.execute("SELECT * FROM notes WHERE title=?", (title,))
        note = self.cursor.fetchone()
        # print the note
        return note

    def update_single_note(self,title, text, date, tags):
        # update a single note
        self.cursor.execute("UPDATE notes SET text=?, date=?, tags=? WHERE title=?", (text, date, tags, title))
        # commit the changes
        self.conn.commit()

    def delete_single_note(self, title):
        # delete a single note
        self.cursor.execute("DELETE FROM notes WHERE title=?", (title,))
        # commit the changes
        self.conn.commit()

    def reset_table(self):
        # drop the table
        self.cursor.execute(f"DROP TABLE {self.name}")
        # commit the changes
        self.connection.commit()

    def close_connection(self):
        # close the connection
        self.connection.close()
        
# to restart the database run this function
'''reset_table()
create_table()
'''