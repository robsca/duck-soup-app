import tkinter as tk
from c_Text_Editor import TextEditor
from d_Database_Manager import database

class NoteApp:
    def __init__(self, root):
        self.root = root
        # initialize database
        self.database = database('notes.db')

    def list_of_notes(self):
        # get all notes
        notes = self.database.get_all_notes()
        # all the notes in a listbox
        self.listbox_notes = tk.Listbox(self.root, height=5, width=20)
        self.listbox_notes.grid(row=0, column=8, sticky="nsew", padx=5, pady=5)
        # insert all the notes in the listbox
        for note in notes:
            # title is the first element in the tuple
            self.listbox_notes.insert(tk.END, note[0])

        # create button to delete listbox
        def delete_listbox():
            self.listbox_notes.destroy()
            delete_button.destroy()

        delete_button = tk.Button(self.root, text="Hide", command=lambda: delete_listbox())
        delete_button.grid(row=1, column=8, sticky="nsew", padx=5, pady=5)

    def save_note(self):
        # get the title from the text editor
        title = self.text_editor.title_entry.get()
        # get the text from the text editor
        text = self.text_editor.get_text()
        # save the note
        self.database.new_note(title, text, 'date', 'tags')
        
    def write(self):
        # create a button to 
        button_all_notes = tk.Button(self.root, text="All Notes", command=lambda: self.list_of_notes())
        button_all_notes.grid(row=2, column=8, sticky="nsew", padx=5, pady=5)
        self.text_editor = TextEditor(self.root)
        self.text_editor.text_entry.focus()
        # create a button to save the note
        button_save = tk.Button(self.root, text="Save", command=lambda: self.save_note())
        button_save.grid(row=3, column=8, sticky="nsew", padx=5, pady=5)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Note App")
    root.geometry("800x600")
    note_app = NoteApp(root)
    note_app.write()
    note_app.run()

        

