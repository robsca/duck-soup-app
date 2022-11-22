from os import truncate
from helper_functions import *
import tkinter as tk
import sqlite3
from manage_database import get_tag_and_words
from transformers import pipeline
import datetime as datetime
from model_tgen import model, tokenizer


import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # to plot in tkinter

# create a connection to the database
connection = sqlite3.connect("notes.db")
cursor = connection.cursor()

# create a tkinter window
window = tk.Tk()
window.title("Nemo")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}") # 10% less

# get all notes and print them
def get_all_notes():
    # create a listbox
    listbox = tk.Listbox(window, width=35, height=30)
    listbox.config(highlightthickness=0,
               bd=0,
                relief='flat',
                bg=window.cget("bg"),
                width=35, height=30,font=("Arial", 12),
                activestyle='none',
                # get backgroung color of the window
                selectbackground='#e8e8e8',
                highlightbackground='#e8e8e8',
                highlightcolor='#e8e8e8',
                selectborderwidth=0,
                selectmode=tk.SINGLE,
    )
    listbox.grid(row=2, column=0, padx=50, pady=50)
    # get all notes
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    for i, note in enumerate(notes):
        title = note[0]
        text = note[1]
        date = note[2]
        tags = note[3]
        listbox.insert(tk.END, f"{title} - {date} - {tags}")
        

        def delete_note(title):
            cursor.execute("DELETE FROM notes WHERE title = ?", (title,))
            connection.commit()
            get_all_notes()

        def edit_note(title):
            edit_window = tk.Tk()
            edit_window.title("Edit Note")
            screen_width = edit_window.winfo_screenwidth()
            screen_height = edit_window.winfo_screenheight()
            edit_window.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}")
            # get the note
            cursor.execute("SELECT * FROM notes WHERE title = ?", (title,))
            note = cursor.fetchone()
            # create the title entry
            title_entry = tk.Entry(edit_window, width=50)
            title_entry.grid(row=0, column=0, padx=50, pady=50)
            title_entry.insert(0, note[0])
            # create the text entry
            text_entry = tk.Text(edit_window, width=50, height=30)
            text_entry.grid(row=1, column=0, padx=50, pady=50)
            text_entry.insert(tk.END, note[1])
            # create the tags entry
            tags_entry = tk.Entry(edit_window, width=50)
            tags_entry.grid(row=2, column=0, padx=50, pady=50)
            tags_entry.insert(0, note[3])
            # create the save button
            save_button = tk.Button(edit_window, text="Save", command=lambda: save_note(title))
            save_button.grid(row=3, column=0, padx=50, pady=50)
            # save the note
            def save_note(title):
                # get the new values
                new_title = title_entry.get()
                new_text = text_entry.get("1.0", tk.END)
                new_tags = tags_entry.get()
                # update the note
                cursor.execute("UPDATE notes SET title = ?, text = ?, tags = ? WHERE title = ?", (new_title, new_text, new_tags, title))
                connection.commit()
                edit_window.destroy()
                get_all_notes()
        
        def open_notes(title):
            print(title)

            # create a new window
            note_window = tk.Tk()
            note_window.title("Note")
            screen_width = note_window.winfo_screenwidth()
            screen_height = note_window.winfo_screenheight()
            note_window.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}")
            # get the note
            cursor.execute("SELECT * FROM notes WHERE title = ?", (title,))
            note = cursor.fetchone()
            # create the title label
            title_label = tk.Label(note_window, text=note[0], font=("Arial", 20))
            title_label.grid(row=0, column=0, padx=50, pady=50)
            # create the text label
            text_label = tk.Label(note_window, text=note[1], font=("Arial", 12))
            text_label.grid(row=1, column=0, padx=50, pady=50)
            # create the tags label
            tags_label = tk.Label(note_window, text=note[3], font=("Arial", 12))
            tags_label.grid(row=2, column=0, padx=50, pady=50)
            # create the delete button
            delete_button = tk.Button(note_window, text="Delete", command=lambda: delete_note(title))
            delete_button.grid(row=3, column=0, padx=50, pady=50)
            # create the edit button
            edit_button = tk.Button(note_window, text="Edit", command=lambda: edit_note(title))
            edit_button.grid(row=4, column=0, padx=50, pady=50)

        def onselect(evt):
            # get the index of the selected note
            w = evt.widget
            index = int(w.curselection()[0])
            value = w.get(index)
            # get the title of the selected note
            title = value.split(" - ")[0]
            # get the date of the selected note
            date = value.split(" - ")[1]
            # get the tags of the selected note
            tags = value.split(" - ")[2]
            # place edit and delete button for every note
            edit_button = tk.Button(window, text="Edit", command=lambda: edit_note(title))
            # place it in the grid
            edit_button.grid(row=0, column=1, padx=10, pady=10)
            delete_button = tk.Button(window, text="Delete", command=lambda: delete_note(title))
            # place it in the grid
            delete_button.grid(row=0, column=2, padx=10, pady=10)

        def on_double_click(evt):
            w = evt.widget
            index = int(w.curselection()[0])
            value = w.get(index)
            # get the title of the selected note
            title = value.split(" - ")[0]
            # get the date of the selected note
            date = value.split(" - ")[1]
            # get the tags of the selected note
            tags = value.split(" - ")[2]
            # open the note
            open_notes(title)

        listbox.bind("<Double-Button-1>", on_double_click)
        listbox.bind('<<ListboxSelect>>', onselect)

        def plot(df):
            # create a frame to plot a matplotlib graph
            window_for_graph = tk.Tk()
            window_for_graph.geometry("800x800")
            window_for_graph.title("Graph")
            frame = tk.Frame(window_for_graph)
            frame.grid(row=4, column=0, columnspan=4)
            G = nx.from_pandas_edgelist(df, 'tag', 'words', create_using=nx.Graph())
            print('G is a graph with {} nodes and {} edges'.format(G.number_of_nodes(), G.number_of_edges()))
            # import the figurecanvastkagg backend
            # create a figure
            fig = plt.figure(figsize=(8, 8))
            # create a canvas
            canvas = FigureCanvasTkAgg(fig, master=frame)

            # create a subplot
            ax = fig.add_subplot(111)
            # plot the graqph node and edge
            nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, ax=ax)
            # place the canvas on the window
            canvas.draw()
            # pack the canvas
            canvas.get_tk_widget().pack()

    # if command + p is pressed plot the graph
    def plot_graph(event):
          # graph
        cursor.execute("SELECT tags FROM notes")
        tags = cursor.fetchall()
        df = get_tag_and_words(tags)
        plot(df)

    # bind the plot_graph function to the command + p key
    window.bind("<Command-p>", plot_graph)
    
# create a new note
def new_note():
    # create a new window
    new_note_window = tk.Tk()
    new_note_window.title("New note")
    new_note_window.geometry(f"{int(screen_width*0.71)}x{int(screen_height*0.9)}") # 25% less
    width = new_note_window.winfo_screenwidth()
    
    value=datetime.datetime.now().strftime("%d-%m-%Y")
    date_entry = tk.Entry(new_note_window, textvariable=value)
    title_entry = tk.Entry(new_note_window)
  
    text_entry = tk.Text(new_note_window, width=width//10, height=50)
    text_entry.grid(row=1, column=0, columnspan=4, padx=10, pady=10)
    ''''''

    def generate_text_from_prompt(event):
        prompt = text_entry.get("1.0", "end-1c")
        # get last word of prompt
        last_word = prompt.split()[-1]
        len_prompt = len(prompt.split())
        print(last_word[:6])
        # get length of prompt
        if last_word == "/gen200":
            print("Generating 200 words")
            # delete last word from prompt
            prompt = prompt.replace(last_word, "")
            
            input_ids = tokenizer.encode(prompt, return_tensors='pt')
            sample_outputs = model.generate(input_ids, do_sample=True, max_length= len_prompt + 200)
           
            # print sample outputs
            generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
            # delete textarea
            text_entry.delete(1.0, tk.END)
            return generated_text
        elif last_word == "/gen50":
            print("Generating 50 words")
            # delete last word from prompt
            prompt = prompt.replace(last_word, "")
            # encode context the generation is conditioned on
            input_ids = tokenizer.encode(prompt, return_tensors='pt')
            sample_outputs = model.generate(input_ids, do_sample=True, max_length=50)
            # print sample outputs
            generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
            # delete textarea
            text_entry.delete(1.0, tk.END)
            return generated_text
        elif last_word == "/gen100":
            print("Generating 100 words")
            # delete last word from prompt
            prompt = prompt.replace(last_word, "")
            # encode context the generation is conditioned on
            input_ids = tokenizer.encode(prompt, return_tensors='pt')
            sample_outputs = model.generate(input_ids, do_sample=True, max_length=100)
            # print sample outputs
            generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
            # delete textarea
            text_entry.delete(1.0, tk.END)
            return generated_text
        elif last_word == "/summary":
            # delete last word from prompt
            prompt = prompt.replace(last_word, "")
            print("Generating summary") 
            summarizer = pipeline("summarization")

            summary = summarizer(prompt, max_length=100, min_length=30, truncation=True)
            summary = summary[0]['summary_text']
            # add summary to textarea
            text_entry.insert(tk.END, summary)
            
            
        elif last_word[:6] == "/wiki(":
            # make a request to wikipedia
            print("Getting wikipedia summary")
            # get the word to search
            word = last_word[6:-1]
            # delete last word from prompt
            prompt = prompt.replace(last_word, "")
            # if is only one word
            if len(word.split()) != 1:
                word = word.replace(" ", "_")
            url = "https://en.wikipedia.org/wiki/" + word
            text_from_wikipedia = web_scrape_webpage(url)
            text_entry.insert(tk.END, text_from_wikipedia)
        else:
            print('No generate command found')

    text_entry.bind('<Return>', lambda event: text_entry.insert(tk.END, generate_text_from_prompt(text_entry)))

        # create shortcuts to delete the current line
    def delete_line(event):
        text_entry.delete("insert linestart", "insert lineend +1c")
    text_entry.bind("<Command-d>", delete_line)

    tags_entry = tk.Entry(new_note_window)
    # create a label to show the title
    # create a button to create a new note
    create_note_button = tk.Button(new_note_window, text="Create note")
    title_entry.grid(row=0, column=0, sticky="sw")
    date_entry.grid(row=0, column=3, sticky="se")
    tags_entry.grid(row=2, column=0, sticky="sw")
    # create note has to be sticky in the middle

    # save the note
    def save_note_and_plot(destroy=True):
        # get the title, text and date
        title = title_entry.get()
        text = text_entry.get(index1="1.0", index2="end")
        date = date_entry.get()
        tags = tags_entry.get()

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

    # save the note
    def save_note(destroy=True):
        # get the title, text and date
        title = title_entry.get()
        text = text_entry.get(index1="1.0", index2="end")
        date = date_entry.get()
        tags = tags_entry.get()

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
            # close the window
            new_note_window.destroy()
            # get all notes
            get_all_notes()
            # create a window to show the note
            note_window = tk.Tk()
            note_window.title(title)
            note_window.geometry("500x300")
            # create a label to show the title
            title_label = tk.Label(note_window, text=title)
            title_label.grid(row=0, column=0)
            # create a label to show the text
            text_label = tk.Label(note_window, text=text)
            text_label.grid(row=1, column=0)
            # create a label to show the date
            date_label = tk.Label(note_window, text=date)
            date_label.grid(row=2, column=0)
            # create a label to show the tags
            tags_label = tk.Label(note_window, text=tags)
            tags_label.grid(row=3, column=0)

            # create a button to close the window
            close_button = tk.Button(note_window, text="Close", command=note_window.destroy)
            close_button.grid(row=3, column=0)

    # create a button to save the note
    # bind the save_note function to the create_note_button
    create_note_button.config(command=save_note)
    create_note_button.grid(row=2, column=2, sticky="sew")

    # check how many words are in the text
    def count_words():
        text = text_entry.get(index1="1.0", index2="end")
        words = text.split()
        word_count = len(words)
        word_count_label = tk.Label(new_note_window, text=f"Word count: {word_count}")
        word_count_label.grid(row=2, column=0, columnspan=3)

        # analyze the text
        def analyze_text():
            from nltk.corpus import stopwords
            no_words = stopwords.words("english")
            from collections import Counter

            words = text.split() # split the text into words
            words = [word.strip(".,!?:;") for word in words] # strip the words from the symbols
            words = [word for word in words if word not in no_words]  # take out the no words
            word_count = Counter(words)
            # get the most common words
            most_common_words = word_count.most_common(5)
            most_common_words_label = tk.Label(new_note_window, text=f"Most common words: {most_common_words}")
            most_common_words_label.grid(row=3, column=0, columnspan=4)
        
        analyze_text()
        
    def plot(df):
      
        # create a frame to plot a matplotlib graph
        window_for_graph = tk.Tk()
        window_for_graph.geometry("800x800")
        window_for_graph.title("Graph")
        frame = tk.Frame(window_for_graph)
        frame.grid(row=4, column=0, columnspan=4)
        G = nx.from_pandas_edgelist(df, 'tag', 'words', create_using=nx.Graph())
        print('G is a graph with {} nodes and {} edges'.format(G.number_of_nodes(), G.number_of_edges()))
        # import the figurecanvastkagg backend
        # create a figure
        fig = plt.figure(figsize=(8, 8))
        # create a canvas
        canvas = FigureCanvasTkAgg(fig, master=frame)

        # create a subplot
        ax = fig.add_subplot(111)
        # plot the graph
        nx.draw(G, with_labels=True, ax=ax)
        # show the plot
        canvas.draw()
        # pack the canvas
        canvas.get_tk_widget().pack()

    # if command + p is pressed plot the graph
    def plot_graph(event):
          # graph
        cursor.execute("SELECT tags FROM notes")
        tags = cursor.fetchall()
        # save the new note in the database
        save_note_and_plot()
        df = get_tag_and_words(tags)
        plot(df)

    # bind the plot_graph function to the command + p key
    new_note_window.bind("<Command-p>", plot_graph)
    
    # every time_ the text changes, count the words
    text_entry.bind("<KeyRelease>", lambda event: count_words())

    # create a button to read the note
    def read_note():
        # get the text
        text = text_entry.get(index1="1.0", index2="end")
        text_to_speech(text)

        '''here is the code for the text to speech - needs adjustments!''' 
        
    read_note_button = tk.Button(new_note_window, text="Read note", command=read_note)
    read_note_button.grid(row=4, column=0, sticky="w")

# Logic
if __name__ == "__main__":
    # Get all notes for the main page
    get_all_notes()

    # Create a button to create a new note
    new_note_button = tk.Button(window, text="+", command=new_note)
    new_note_button.grid(row=0, column=0, sticky="w")

    # run the mainloop
    window.mainloop()