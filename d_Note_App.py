import tkinter as tk
from b_Text_Editor import TextEditor

class NoteApp:
    def __init__(self, root):
        self.root = root

    def write(self):
        self.text_editor = TextEditor(self.root)
        self.text_editor.text_entry.focus()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Note App")
    root.geometry("800x600")
    note_app = NoteApp(root)
    note_app.write()
    note_app.run()

        

