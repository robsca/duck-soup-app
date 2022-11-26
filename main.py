from helper_functions import *
from manage_database import get_tag_and_words

import tkinter as tk
import sqlite3
from transformers import pipeline
summarizer = pipeline("summarization")

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
    save_button.grid(row=0, column=3)
    
    # FUNCTIONS NLP
    def generate_text(num, prompt):
        print(f"Generating {num} words")
        len_prompt = len(prompt.split())
        last_word = prompt.split()[-1]
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        sample_outputs = model.generate(input_ids, do_sample=True, max_length= len_prompt + num)
        
        # print sample outputs
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        # delete textarea
        text_entry.delete(1.0, tk.END)
        # insert generated text
        text_entry.insert(tk.END, generated_text)

    def create_summary(prompt, max_length=100, min_length=30, delete_prompt=True):
            # delete last word from prompt
            last_word = prompt.split()[-1]
            prompt = prompt.replace(last_word, "")
            print("Generating summary") 
            summarizer = pipeline("summarization")

            summary = summarizer(prompt, max_length=max_length, min_length=min_length, truncation=True)
            summary = summary[0]['summary_text']
            # add summary to textarea
            text_entry.insert(tk.END, summary)

    def get_wiki_summary(prompt,last_word):
        # make a request to wikipedia
        print("Getting wikipedia summary")
        # get the word to search
        word = last_word[6:]
        # if + is in the word
        if "+" in word:
            word_ = word.split("+")[0]
            chapter_ = word.split("+")[1]
            print(f"Getting chapter {chapter_} of {word_}")
            url = f"https://en.wikipedia.org/wiki/{word_}"
            text, chapters = get_wiki_text(url, chapter_)
            # replace the / with a space
            text = text.replace("/", " ")
            prompt = prompt.replace(last_word, text)
            # delete textarea
            text_entry.delete(1.0, tk.END)
            # insert generated text
            text_entry.insert(tk.END, prompt)

        else:
            chapter_ = None
            url = f"https://en.wikipedia.org/wiki/{word}"
            text, chapters = get_wiki_text(url)
            # replace the / with a space
            text = text.replace("/", " ")
            print(text)
            print(chapters)
            # create a new window
            wiki_window = tk.Toplevel(edit_window)
            wiki_window.title("Wikipedia")
            wiki_window.geometry("350x350")
            # add text to textarea
            text_entry.insert(tk.END, text)
            # add chapters to listbox
            listbox = tk.Listbox(wiki_window, height=10, width=40)
            listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            for chapter in chapters:
                listbox.insert(tk.END, chapter)
            
            # if chapter is selected
            def select_chapter(event):
                # get selected chapter
                chapter = listbox.get(listbox.curselection())
                # get text from wikipedia
                text, chapters = get_wiki_text(url, chapter)
                # replace the / with a space
                text = text.replace("/", " ")
                # delete textarea
                text_entry.delete(1.0, tk.END)
                # insert generated text
                text_entry.insert(tk.END, text)
                # destroy window
                wiki_window.destroy()
            # bind event to listbox
            listbox.bind("<<ListboxSelect>>", select_chapter)

    def question_answering(prompt):
        def answer_question(prompt):
            model = pipeline("question-answering")
            question = question_entry.get("1.0", "end-1c")
            answer = model(question=question, context=prompt)
            answer_entry.insert(tk.END, answer['answer'])

        # create a new window
        qa_window = tk.Toplevel(edit_window)
        qa_window.title("Question Answering")
        qa_window.geometry("350x350")
        # question entry
        question_entry = tk.Text(qa_window, height=10, width=40)
        question_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        # answer entry
        answer_entry = tk.Text(qa_window, height=10, width=40)
        answer_entry.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        # answer button
        answer_button = tk.Button(qa_window, text="Answer", command=lambda: answer_question(prompt))
        answer_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        # close button
        def close_window():
            # delete /qa from prompt
            # get text from text_entry
            text = text_entry.get("1.0", "end-1c")
            # delete last word from prompt
            last_word = text.split()[-1]
            text = text.replace(last_word, "")
            # delete textarea
            text_entry.delete(1.0, tk.END)
            # insert generated text
            text_entry.insert(tk.END, text)

            qa_window.destroy()
        close_button = tk.Button(qa_window, text="Close", command=close_window)
        close_button.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

    # EVENTS
    def interpreter(event):
        prompt = text_entry.get("1.0", "end-1c")
        # get last word of prompt
        last_word = prompt.split()[-1]


        # text generation
        if last_word == "/gen200":
            generate_text(200, prompt)
        elif last_word == "/gen50":
            generate_text(50, prompt)
        elif last_word == "/gen100":
            generate_text(100, prompt)
        # summary
        elif last_word == "/summary":
            create_summary(prompt)
        # wikipedia scraping
        elif last_word[:6] == "/wiki-":
            get_wiki_summary(prompt, last_word)
        # question answering
        elif last_word == "/qa":
            question_answering(prompt)
        else:
            print('No generate command found')

        return None

    # if text is highlighted, delete it when pressed command + s
    def summary_highlighted_text(event):
        '''
        This function is called when the user presses command + s
        It creates a summary of the highlighted text and replaces it with the summary
        '''
        # get selected text
        prompt = text_entry.selection_get()
        
        # delete last word from prompt
        print("Generating summary") 
        summarizer = pipeline("summarization")

        summary = summarizer(prompt, max_length=100, min_length=30, truncation=True)
        summary = summary[0]['summary_text']

        # put instead of selected text
        text_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        text_entry.insert(tk.INSERT, summary)    

    # every new char excecute a function thtat if is a /
    def is_command(event):
        '''
        This function is called every time a new character is inserted in the text area
        It handles the styling of the text if it is a command
        '''
        # check if '/' is in text
        prompt = text_entry.get("1.0", "end-1c")
        if '/' in prompt:
            print("Command found")
            # get index of '/'
            index = prompt.index('/')
            # change the color of the text until the end
            text_entry.tag_add("command", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("command", foreground="grey")
            # make it bold
            text_entry.tag_add("bold", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("bold", font="bold")
            # make it bigger
            text_entry.tag_add("big", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("big", font=("Helvetica", 20))
        else:
            #print("No command found")
            text_entry.tag_delete("command")
            text_entry.tag_delete("bold")
            text_entry.tag_delete("big")

        text = text_entry.get(index1="1.0", index2="end")
        words = text.split()
        word_count = len(words)
        word_count_label = tk.Label(edit_window, text=f"Word count: {word_count}")
        word_count_label.grid(row=2, column=0)

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
            most_common_words_label = tk.Label(edit_window, text=f"Most common words: {most_common_words}")
            most_common_words_label.grid(row=0, column=3, columnspan=4)
        
        analyze_text()

    # BINDINGS
    text_entry.bind('<KeyRelease>', is_command)
    text_entry.bind('<Return>', lambda event: text_entry.insert(tk.END, interpreter(text_entry)))
    text_entry.bind('<Control-s>', summary_highlighted_text)

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
    # print
    print("Title: ", note[0])
    # create the title label
    title_label = tk.Label(note_window, text=note[0], font=("Arial", 20))
    title_label.grid(row=0, column=0, padx=50, pady=50)
    # create the text label
    text_label = tk.Label(note_window, text=note[1], font=("Arial", 12))
    # auto wrap the text
    text_label.config(wraplength=screen_width*0.9)
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

    for _, note in enumerate(notes):
        title = note[0]
        date = note[2]
        tags = note[3]
        listbox.insert(tk.END, f"{date} - {title} - {tags}")

        def onselect(evt):
            # get the index of the selected note
            w = evt.widget
            index = int(w.curselection()[0])
            value = w.get(index)
            # get the title of the selected note
            title = value.split(" - ")[1]
            # get the date of the selected note
            date = value.split(" - ")[0]
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
            title = value.split(" - ")[1]
            # get the date of the selected note
            date = value.split(" - ")[0]
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
    # set the size of the window
    new_note_window.geometry(f"{int(screen_width*0.71)}x{int(screen_height*0.9)}") # 25% less
    width = new_note_window.winfo_screenwidth()
    # Create all the entries for a note objects
    # date entry 
    value=datetime.datetime.now().strftime("%d-%m-%Y")
    date_entry = tk.Entry(new_note_window)
    date_entry.insert(0, value)
    # set color of the entry as color of main no border color and no border width
    date_entry.config(bg=window.cget("bg"), highlightbackground=window.cget("bg"), highlightthickness=0, borderwidth=0)
    # title entry transparent
    title_entry = tk.Entry(new_note_window)
    # color of the widget is get color of the window and no border
    title_entry.config(bg=window.cget("bg"), highlightbackground=window.cget("bg"), highlightthickness=0, borderwidth=0)
    # add a placeholder
    title_entry.insert(0, "Title")
    # text entry
    text_entry = tk.Text(new_note_window, width=width//10, height=50)
    # set a padding for the text entry
    text_entry.config(wrap="word", padx=10, pady=10)
    # tags entry
    tags_entry = tk.Entry(new_note_window)
    # add some padding to the tags entry
    tags_entry.config(bg=window.cget("bg"), highlightbackground=window.cget("bg"), highlightthickness=0, borderwidth=0)
    # add a placeholder
    tags_entry.insert(0, "Tags")
    # create a submit button
    create_note_button = tk.Button(new_note_window, text="Create note")
    ''''''

    # FUNCTIONS NLP
    def generate_text(num, prompt):
        print(f"Generating {num} words")
        len_prompt = len(prompt.split())
        last_word = prompt.split()[-1]
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        sample_outputs = model.generate(input_ids, do_sample=True, max_length= len_prompt + num)
        
        # print sample outputs
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        # delete textarea
        text_entry.delete(1.0, tk.END)
        # insert generated text
        text_entry.insert(tk.END, generated_text)

    def create_summary(prompt, max_length=100, min_length=30, delete_prompt=True):
            # delete last word from prompt
            last_word = prompt.split()[-1]
            prompt = prompt.replace(last_word, "")
            print("Generating summary") 
            summarizer = pipeline("summarization")

            summary = summarizer(prompt, max_length=max_length, min_length=min_length, truncation=True)
            summary = summary[0]['summary_text']
            # add summary to textarea
            text_entry.insert(tk.END, summary)

    def get_wiki_summary(prompt,last_word):
        # make a request to wikipedia
        print("Getting wikipedia summary")
        # get the word to search
        word = last_word[6:]
        # if + is in the word
        if "+" in word:
            word_ = word.split("+")[0]
            chapter_ = word.split("+")[1]
            print(f"Getting chapter {chapter_} of {word_}")
            url = f"https://en.wikipedia.org/wiki/{word_}"
            text, chapters = get_wiki_text(url, chapter_)
            # replace the / with a space
            text = text.replace("/", " ")
            prompt = prompt.replace(last_word, text)
            # insert generated text
            text_entry.insert(tk.END, prompt)
        else:
            chapter_ = None
            url = f"https://en.wikipedia.org/wiki/{word}"
            text, chapters = get_wiki_text(url)
            # replace the / with a space
            text = text.replace("/", " ")
            print(text)
            print(chapters)
            # create a new window
            wiki_window = tk.Toplevel(window)
            wiki_window.title("Wikipedia")
            wiki_window.geometry("350x350")
            # before adding the text check the text_entry and save the text
            before_wiki = text_entry.get(1.0, tk.END)
            text_entry.insert(tk.END, text)
            # add chapters to listbox
            listbox = tk.Listbox(wiki_window, height=10, width=40)
            listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            for chapter in chapters:
                listbox.insert(tk.END, chapter)
            
            # if chapter is selected
            def select_chapter(event):
                # get selected chapter
                chapter = listbox.get(listbox.curselection())
                # get text from wikipedia
                text, chapters = get_wiki_text(url, chapter)
                # add before_wiki to to text_entry
                text_entry.delete(1.0, tk.END)
                text_entry.insert(tk.END, before_wiki)
                # replace the / with a space
                text = text.replace("/", " ")
                # insert generated text
                text_entry.insert(tk.END, text)
                # destroy window
                wiki_window.destroy()
            # bind event to listbox
            listbox.bind("<<ListboxSelect>>", select_chapter)

    def get_url_text(prompt, last_word):
        # get the url
        url = last_word[5:]
        # make a request to the url
        print("Getting url text")
        text = get_text_from_url(url)
        # replace the / with a space
        text = text.replace("/", " ")
        # insert generated text
        text_entry.insert(tk.END, text)
    
    def question_answering(prompt):
        def answer_question(prompt):
            model = pipeline("question-answering")
            question = question_entry.get("1.0", "end-1c")
            answer = model(question=question, context=prompt)
            answer_entry.insert(tk.END, answer['answer'])

        # create a new window
        qa_window = tk.Toplevel(window)
        qa_window.title("Question Answering")
        qa_window.geometry("350x350")
        # question entry
        question_entry = tk.Text(qa_window, height=10, width=40)
        question_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        # answer entry
        answer_entry = tk.Text(qa_window, height=10, width=40)
        answer_entry.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        # answer button
        answer_button = tk.Button(qa_window, text="Answer", command=lambda: answer_question(prompt))
        answer_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        # close button
        def close_window():
            # delete /qa from prompt
            # get text from text_entry
            text = text_entry.get("1.0", "end-1c")
            # delete last word from prompt
            last_word = text.split()[-1]
            text = text.replace(last_word, "")
            # delete textarea
            text_entry.delete(1.0, tk.END)
            # insert generated text
            text_entry.insert(tk.END, text)

            qa_window.destroy()
        close_button = tk.Button(qa_window, text="Close", command=close_window)
        close_button.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

    # EVENTS
    def interpreter(event):
        # 1. get text from text_entry
        prompt = text_entry.get("1.0", "end-1c")
        # 2. get last word from prompt
        last_word = prompt.split()[-1]

        # ACTIONS FOR LAST WORD
        if last_word == "/gen200":
            # generate text
            generate_text(200, prompt)
        elif last_word == "/gen50":
            generate_text(50, prompt)
        elif last_word == "/gen100":
            generate_text(100, prompt)
        # summary
        elif last_word == "/summary":
            create_summary(prompt)
        # wikipedia scraping
        elif last_word[:6] == "/wiki-":
            get_wiki_summary(prompt, last_word)
        # url scraping
        elif last_word[:5] == "/url-":
            get_url_text(prompt, last_word)
        # question answering
        elif last_word == "/qa":
            question_answering(prompt)
        else:
            print('No generate command found')
        return None

    def summary_highlighted_text(event):
        '''
        This function is called when the user presses command + s
        It creates a summary of the highlighted text and replaces it with the summary
        '''
        # get selected text
        prompt = text_entry.selection_get()
        
        # delete last word from prompt
        print("Generating summary") 

        summary = summarizer(prompt, max_length=100, min_length=30, truncation=True)
        summary = summary[0]['summary_text']

        # put instead of selected text
        text_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        text_entry.insert(tk.INSERT, summary)    

    def is_command(event):
        '''
        This function is called every time a new character is inserted in the text area
        It handles the styling of the text if it is a command
        '''
        # check if '/' is in text
        prompt = text_entry.get("1.0", "end-1c")
        if '/' in prompt:
            print("Command found")
            # get index of '/'
            index = prompt.index('/')
            # change the color of the text until the end
            text_entry.tag_add("command", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("command", foreground="grey")
            # make it bold
            text_entry.tag_add("bold", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("bold", font="bold")
            # make it bigger
            text_entry.tag_add("big", "1.0 + " + str(index) + "c", "end")
            text_entry.tag_config("big", font=("Helvetica", 20))
        else:
            #print("No command found")
            text_entry.tag_delete("command")
            text_entry.tag_delete("bold")
            text_entry.tag_delete("big")

        text = text_entry.get(index1="1.0", index2="end")
        words = text.split()
        word_count = len(words)
        word_count_label = tk.Label(new_note_window, text=f"Word count: {word_count}")
        word_count_label.grid(row=2, column=0)

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
            most_common_words_label.grid(row=0, column=3, columnspan=4)
        
        analyze_text()

    def delete_line(event):
        text_entry.delete("insert linestart", "insert lineend +1c")

    # DATABASE FUNCTIONS
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
    
    def plot_graph(event):
          # graph
        cursor.execute("SELECT tags FROM notes")
        tags = cursor.fetchall()
        # save the new note in the database
        save_note_and_plot()
        df = get_tag_and_words(tags)
        plot(df)

    # BINDINGS Functions
    text_entry.bind('<Return>', lambda event: text_entry.insert(tk.END, interpreter(text_entry)))
    text_entry.bind("<Command-d>", delete_line) # shortcut for deleting a line
    text_entry.bind('<KeyRelease>', is_command) # check if a command is inserted
    text_entry.bind('<Control-s>', summary_highlighted_text) # shortcut for summarizing highlighted text
    new_note_window.bind("<Command-p>", plot_graph)
    create_note_button.config(command=save_note)

    # GRID
    title_entry.grid(row=0, column=0, sticky="sw", padx=10, pady=10)
    date_entry.grid(row=0, column=3, sticky="se", padx=10, pady=10)
    tags_entry.grid(row=2, column=0, sticky="sw", padx=10, pady=10)
    text_entry.grid(row=1, column=0, columnspan=4, padx=10, pady=10)
    create_note_button.grid(row=2, column=2, sticky="sew", padx=10, pady=10)

'''Logic'''
if __name__ == "__main__":
    # Get all notes for the main page
    get_all_notes()

    # Create a button to create a new note
    new_note_button = tk.Button(window, text="+", command=new_note)
    new_note_button.grid(row=0, column=0, sticky="w")

    # run the mainloop
    window.mainloop()