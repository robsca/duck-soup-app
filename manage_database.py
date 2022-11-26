# import the sqlite3 module
import sqlite3

# create a connection to the database
connection = sqlite3.connect("notes.db")

# create a cursor
cursor = connection.cursor()

def create_table():
    # create a table
    cursor.execute("CREATE TABLE notes (title TEXT, text TEXT, date TEXT, tags TEXT)")

def new_note(title, text, date, tags):
    # title need to be unique check it first
    cursor.execute("SELECT * FROM notes WHERE title=?", (title,))
    note = cursor.fetchone()
    if note:
        print("Note already exists")
    else:
        # create a new note
        cursor.execute("INSERT INTO notes VALUES (?, ?, ?, ?)", (title, text, date, tags))
        # commit the changes
        connection.commit()

def get_all_notes():
    # try to open the notes table
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    # print the notes
    for note in notes:
        print(note)

def get_single_note(title):
    # get a single note
    cursor.execute("SELECT * FROM notes WHERE title=?", (title,))
    note = cursor.fetchone()
    # print the note
    print(note)

def update_single_note(title, text, date, tags):
    # update a single note
    cursor.execute("UPDATE notes SET text=?, date=?, tags=? WHERE title=?", (text, date, tags, title))
    # commit the changes
    connection.commit()

def delete_single_note(title):
    # delete a single note
    cursor.execute("DELETE FROM notes WHERE title=?", (title,))
    # commit the changes
    connection.commit()

# get all notes from date to date
def get_notes_from_date_to_date(date1, date2):
    # get all notes from date to date
    cursor.execute("SELECT * FROM notes WHERE date BETWEEN ? AND ?", (date1, date2))
    notes = cursor.fetchall()
    # print the notes
    for note in notes:
        print(note)

def reset_table():
    # drop the table
    cursor.execute("DROP TABLE notes")
    # commit the changes
    connection.commit()

# for networkx graphs
def get_tag_and_words(tags):
    # create a table with two colums
    import pandas as pd
    df = pd.DataFrame(columns=['tag', 'words'])
    # get all the words for each tag
    for tag in tags:
        # get all the notes for each tag
        cursor.execute("SELECT * FROM notes WHERE tags=?", (tag[0],))
        notes = cursor.fetchall()
        # get all the words for each note
        words = []
        for note in notes:
            words.append(note[1].split())
        # flatten the list
        words = [item for sublist in words for item in sublist]
        # add the tag and the words to the dataframe
        for word in words:
            # use concat to add the new row
            df = pd.concat([df, pd.DataFrame([[tag[0], word]], columns=['tag', 'words'])])
    print(df)
    return df

reset_table()
create_table()
